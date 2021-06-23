import subprocess
import os
import platform
import struct
from dol_c_kit import DolFile, write_uint32
from dol_c_kit import assemble_branch, write_branch, apply_gecko
from dol_c_kit import gecko_04write, gecko_C6write

class Project(object):
    def __init__(self, base_addr=None, verbose=False):
        self.is_built = False
        self.base_addr = base_addr
        
        # System member variables
        self.devkitppc_path = "C:/devkitPro/devkitPPC/bin"
        self.extension = ".exe" if platform.system() == "Windows" else ""
        
        # Compiling member variables
        self.src_dir = "."
        self.obj_dir = "."
        self.project_name = "project"
        self.c_files = []
        self.asm_files = []
        self.obj_files = []
        self.linker_script_files = []
        self.symbols = {}
        self.optimization = "-O1"
        self.c_std = "c99"
        self.verbose = verbose
        
        # Patches member variables
        self.branchlinks = []
        self.branches = []
        self.pointers = []
        self.gecko_txt_files = []
        self.gecko_gct_files = []
        self.osarena_patcher = None
        
        
    def add_c_file(self, filepath):
        self.c_files.append(filepath)
        
    def add_asm_file(self, filepath):
        self.asm_files.append(filepath)
    
    def add_linker_script_file(self, filepath):
        self.linker_script_files.append(filepath)
    
    def add_gecko_txt_file(self, filepath):
        self.gecko_txt_files.append(filepath)
    
#    def add_gecko_gct_file(self, filepath):
#        self.gecko_gct_files.append(filepath)
    
    def add_branch(self, addr, funcname, LK=False):
        self.branches.append((addr, funcname, LK))
    
    def add_branchlink(self, addr, funcname):
        self.add_branch(addr, funcname, LK=True)
    
    def add_pointer(self, addr, funcname):
        self.pointers.append((addr, funcname))
    
    def set_osarena_patcher(self, function):
        self.osarena_patcher = function
    
    def build(self):
        os.makedirs(self.src_dir, exist_ok=True)
        os.makedirs(self.obj_dir, exist_ok=True)
        
        for filepath in self.c_files:
            self.is_built = True
            self.__compile(filepath)
        
        for filepath in self.asm_files:
            self.is_built = True
            self.__assemble(filepath)
        
        if self.is_built == True:
            self.__link_project()
            self.__read_map()
            self.__objcopy_project()
            
            if self.verbose:
                self.__objdump_project()
                print("")
                for key, val in self.symbols.items():
                    print("{0:x} {1:s}".format(val, key))
                print("")
    
    def save_dol(self, in_dol_path, out_dol_path):
        with open(in_dol_path, "rb") as f:
            dol = DolFile(f)
        
        if self.is_built == True:
            with open(self.obj_dir+"/"+self.project_name+".bin", "rb") as f:
                data = f.read()
            
            if dol.is_text_section_available():
                offset, sectionaddr, size = dol.allocate_text_section(len(data), addr=self.base_addr)
            elif dol.is_data_section_available():
                offset, sectionaddr, size = dol.allocate_text_section(len(data), addr=self.base_addr)
            else:
                raise RuntimeError("DOL is full!  Cannot allocate any new sections.")
            
            dol.seek(sectionaddr)
            dol.write(data)
            
            for addr, sym_name, lk_bit in self.branches:
                if sym_name not in self.symbols:
                    print("Undefined Symbol: {0}.  Skipping...".format(sym_name))
                    continue
                if self.verbose:
                    print("Branch{0:s} @ {1:08X} to {2:s}".format("link" if lk_bit else "", addr, sym_name))
                dol.seek(addr)
                write_branch(dol, self.symbols[sym_name], LK=lk_bit)
            
            for addr, sym_name in self.pointers:
                if sym_name not in self.symbols:
                    print("Undefined Symbol: {0}.  Skipping...".format(sym_name))
                    continue
                if self.verbose:
                    print("Pointer @ {0:08x} to {1:s}".format(addr, sym_name))
                dol.seek(addr)
                write_uint32(dol, self.symbols[sym_name])
            
            self.osarena_patcher(dol, self.base_addr + len(data))
        
        self.__apply_gecko(dol)
        
        with open(out_dol_path, "wb") as f:
            dol.save(f)
    
    def save_gecko(self, gecko_path):
        with open(gecko_path, "w") as f:
            if self.is_built == True:
                with open(self.obj_dir+"/"+self.project_name+".bin", "rb") as bin:
                    data = bin.read()
                # Pad new data to next multiple of 8 for the Gecko Codehandler
                len_real = len(data)
                while (len(data) % 8) != 0:
                    data += b'\x00'
            
                f.write("$Program Code\n")
                f.write("{:08X} {:08X}\n".format((self.base_addr & 0x01FFFFFC) | 0x06000000, len_real))
                for i in range(0, len(data), 8):
                    word1 = struct.unpack_from(">I", data, i  )[0]
                    word2 = struct.unpack_from(">I", data, i+4)[0]
                    f.write("{:08X} {:08X}\n".format(word1, word2))
            
            f.write("$Branches\n")
            for addr, sym_name, lk_bit in self.branches:
                if sym_name not in self.symbols:
                    print("Undefined Symbol: {0}.  Skipping...".format(sym_name))
                    continue
                if self.verbose:
                    print("Branch{0:s} @ {1:08X} to {2:s}".format("link" if lk_bit else "", addr, sym_name))
                f.write(gecko_C6write(addr, self.symbols[sym_name], lk_bit) + "\n")
            
            f.write("$Pointers\n")
            for addr, sym_name in self.pointers:
                if sym_name not in self.symbols:
                    print("Undefined Symbol: {0}.  Skipping...".format(sym_name))
                    continue
                if self.verbose:
                    print("Pointer @ {0:08X} to {1:s}".format(addr, sym_name))
                f.write(gecko_04write(addr, self.symbols[sym_name]) + "\n")
    
    def cleanup(self):
        if self.is_built == True:
            for filename in self.obj_files:
                os.remove(self.obj_dir+"/"+filename)
            os.remove(self.obj_dir+"/"+self.project_name+".o")
            os.remove(self.obj_dir+"/"+self.project_name+".bin")
            os.remove(self.obj_dir+"/"+self.project_name+".map")
        self.obj_files.clear()
        self.symbols.clear()
        self.is_built = False
    
    def __compile(self, infile):
        args = [self.devkitppc_path+"/"+"powerpc-eabi-gcc"+self.extension]
        args.append(self.src_dir+"/"+infile)
        args.append("-c")
        args.extend(("-o", self.obj_dir+"/"+infile+".o"))
        args.append(self.optimization)
        args.append("-std="+self.c_std)
        args.append("-w")
        args.extend(("-I", self.src_dir))
        if self.verbose:
            print(args)
        subprocess.call(args)
        self.obj_files.append(infile+".o")
    
    def __assemble(self, infile):
        args = [self.devkitppc_path+"/"+"powerpc-eabi-as"+self.extension]
        args.append(self.src_dir+"/"+infile)
        args.extend(("-o", self.obj_dir+"/"+infile+".o"))
        args.append("-w")
        args.extend(("-I", self.src_dir))
        if self.verbose:
            print(args)
        subprocess.call(args)
        self.obj_files.append(infile+".o")
    
    def __link_project(self):
        if self.base_addr == None:
            raise RuntimeError("ROM end address not set!  New code cannot be linked.")
        
        args = [self.devkitppc_path+"/"+"powerpc-eabi-ld"+self.extension]
        # The symbol "." represents the location counter.  By setting it this way,
        # we don't need a linker script to set the base address of our new code.
        args.extend(("--defsym", ".="+hex(self.base_addr)))
        
        for file in self.linker_script_files:
            args.extend(("-T", file))
        
        args.extend(("-o", self.obj_dir+"/"+self.project_name+".o"))
        
        for filename in self.obj_files:
            args.append(self.obj_dir+"/"+filename)
        
        args.extend(("-Map", self.obj_dir+"/"+self.project_name+".map"))
        if self.verbose:
            print(args)
        subprocess.call(args)
    
    def __objdump_project(self):
        args = [self.devkitppc_path+"/"+"powerpc-eabi-objdump"+self.extension, self.obj_dir+"/"+self.project_name+".o", "--full-content"]
        if self.verbose:
            print(args)
        subprocess.call(args)
    
    def __objcopy_project(self):
        arg = [self.devkitppc_path+"/"+"powerpc-eabi-objcopy"+self.extension]
        arg.append(self.obj_dir+"/"+self.project_name+".o")
        arg.append(self.obj_dir+"/"+self.project_name+".bin")
        arg.extend(("-O", "binary"))
        arg.append("-S")
        arg.extend(("-R", ".eh_frame"))
        arg.extend(("-R", ".comment"))
        arg.extend(("-R", ".gnu.attributes"))
        if self.verbose:
            print(arg)
        subprocess.call(arg)
    
    def __read_map(self):
        with open(self.obj_dir+"/"+self.project_name+".map", "r") as f:
            for next in f:
                if len(next) < 50:
                    continue
                if next[34:50] != "                ":
                    continue
                
                vals = next.strip().split(" ")
                for i in range(vals.count("")):
                    vals.remove("")
                
                addr = vals[0]
                func = vals[1]
                
                self.symbols[func] = int(addr, 16)
    
    def __apply_gecko(self, dol):
        for file in self.gecko_txt_files:
            with open(file, "r") as f:
                apply_gecko(dol, f)
#        for file in self.gecko_gct_files:
#            with open(file, "r") as f:
#                something to process GCT files here
