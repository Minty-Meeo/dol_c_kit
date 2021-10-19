import subprocess
import os
import platform
from dol_c_kit import assemble_branch, write_branch, mask_field, hi, lo, hia

from dolreader.dol import DolFile, write_uint32
from dolreader.section import Section, TextSection, DataSection
from elftools.elf.elffile import ELFFile
from geckolibs.gct import GeckoCodeTable
from geckolibs.geckocode import GeckoCode, GeckoCommand, WriteBranch, Write32, WriteString, Write16


class Hook(object):
    def __init__(self, addr):
        self.good = False
        self.addr = addr
        self.data = None
    
    def resolve(self, symbols):
        return
    
    def apply_dol(self, dol):
        if dol.is_mapped(self.addr):
            self.good = True
    
    def write_geckocommand(self, f):
        self.good = True
        
    def dump_info(self):
        return repr("{:s} {:08X}".format(
                    "{:13s}".format("[Hook]       "), self.addr))[+1:-1]

class BranchHook(Hook):
    def __init__(self, addr, sym_name, lk_bit):
        Hook.__init__(self, addr)
        self.sym_name = sym_name
        self.lk_bit = lk_bit
    
    def resolve(self, symbols):
        if self.sym_name in symbols:
            self.data = symbols[self.sym_name]['st_value']
    
    def apply_dol(self, dol):
        if self.data and dol.is_mapped(self.addr):
            dol.seek(self.addr)
            dol.write(assemble_branch(self.addr, self.data, LK=self.lk_bit))
            self.good = True
    
    def write_geckocommand(self, f):
        if self.data:
            gecko_command = WriteBranch(self.data, self.addr, isLink = self.lk_bit)
            f.write(gecko_command.as_text() + "\n")
            self.good = True
    
    def dump_info(self):
        return repr("{:s} {:08X} {:s} {:s}".format(
                    "[Branchlink] " if self.lk_bit else "[Branch]     ", self.addr, "-->" if self.good else "-X>", self.sym_name))[+1:-1]

class PointerHook(Hook):
    def __init__(self, addr, sym_name):
        Hook.__init__(self, addr)
        self.sym_name = sym_name
    
    def resolve(self, symbols):
        if self.sym_name in symbols:
            self.data = symbols[self.sym_name]['st_value']
    
    def apply_dol(self, dol):
        if self.data and dol.is_mapped(self.addr):
            dol.write_uint32(self.addr, self.data)
            self.good = True
    
    def write_geckocommand(self, f):
        if self.data:
            gecko_command = Write32(self.data, self.addr)
            f.write(gecko_command.as_text() + "\n")
            self.good = True
        
    def dump_info(self):
        return repr("{:s} {:08X} {:s} {:s}".format(
                    "[Pointer]    ", self.addr, "-->" if self.good else "-X>", self.sym_name))[+1:-1]

class StringHook(Hook):
    def __init__(self, addr, string, encoding, max_strlen):
        Hook.__init__(self, addr)
        self.data = bytearray()
        self.string = string
        self.encoding = encoding
        self.max_strlen = max_strlen
    
    def resolve(self, symbols):
        self.data = self.string.encode(self.encoding) + b'\x00'
        if self.max_strlen != None:
            if len(self.data) > self.max_strlen:
                print("Warning: \"{:s}\" exceeds {} bytes!".format(repr(self.string)[+1:-1], self.max_strlen))
            else:
                while len(self.data) < self.max_strlen:
                    self.data += b'\x00'
    
    def apply_dol(self, dol):
        if dol.is_mapped(self.addr):
            dol.seek(self.addr)
            dol.write(self.data)
            self.good = True
    
    def write_geckocommand(self, f):
        gecko_command = WriteString(self.data, self.addr)
        f.write(gecko_command.as_text() + "\n")
        self.good = True
        
    def dump_info(self):
        return repr("{:s} {:08X} {:s} \"{:s}\"".format(
                    "[String]     ", self.addr, "-->" if self.good else "-X>", self.string))[+1:-1]

class FileHook(Hook):
    def __init__(self, addr, filepath, start, end, max_size):
        Hook.__init__(self, addr)
        self.data = bytearray()
        self.filepath = filepath
        self.start = start
        self.end = end
        self.max_size = max_size
    
    def resolve(self, symbols):
        try:
            with open(self.filepath, "rb") as f:
                if self.end == None:
                    self.data = f.read()[self.start:]
                else:
                    self.data = f.read()[self.start:self.end]
                if self.max_size != None:
                    if len(self.data) > self.max_size:
                        print("Warning: \"{:s}\" exceeds {} bytes!".format(repr(self.filepath)[+1:-1], self.max_size))
                    else:
                        while len(self.data) < self.max_size:
                            self.data += b'\x00'
        except OSError:
            print("Warning: \"{:s}\" could not be opened!".format(repr(self.filepath)[+1:-1]))
    
    def apply_dol(self, dol):
        if dol.is_mapped(self.addr):
            dol.seek(self.addr)
            dol.write(self.data)
            self.good = True
    
    def write_geckocommand(self, f):
        gecko_command = WriteString(self.data, self.addr)
        f.write(gecko_command.as_text() + "\n")
        self.good = True
        
    def dump_info(self):
        return repr("{:s} {:08X} {:s} \"{:s}\"".format(
                    "[File]       ", self.addr, "-->" if self.good else "-X>", self.filepath))[+1:-1]

class Immediate16Hook(Hook):
    def __init__(self, addr, sym_name, modifier):
        Hook.__init__(self, addr)
        self.sym_name = sym_name
        self.modifier = modifier
    
    def resolve(self, symbols):
        # I wrote these fancy @h, @l, @ha functions to barely use them, lol.  When writing
        # 16-bit immediates, you don't really need to worry about whether or not it is
        # signed, since you're masking off any sign extension that happens regardless.
        if self.sym_name in symbols:
            if self.modifier == "@h":
                self.data = hi(symbols[self.sym_name]['st_value'], True)
            elif self.modifier == "@l":
                self.data = lo(symbols[self.sym_name]['st_value'], True)
            elif self.modifier == "@ha":
                self.data = hia(symbols[self.sym_name]['st_value'], True)
            elif self.modifier == "@sda":
                if symbols["_SDA_BASE_"]['st_value'] == None:
                    raise RuntimeError("You must set this project's sda_base member before using the @sda modifier!  Check out the set_sda_bases method.")
                self.data = mask_field(symbols[self.sym_name]['st_value'] - symbols["_SDA_BASE_"]['st_value'], 16, True)
            elif self.modifier == "@sda2":
                if symbols["_SDA2_BASE_"]['st_value'] == None:
                    raise RuntimeError("You must set this project's sda2_base member before using the @sda2 modifier!  Check out the set_sda_bases method.")
                self.data = mask_field(symbols[self.sym_name]['st_value'] - symbols["_SDA2_BASE_"]['st_value'], 16, True)
            else:
                print("Unknown modifier: \"{}\"".format(self.modifier))
            self.data = mask_field(self.data, 16, True)
    
    def apply_dol(self, dol):
        if self.data and dol.is_mapped(self.addr):
            dol.write_uint16(self.addr, self.data)
            self.good = True
    
    def write_geckocommand(self, f):
        if self.data:
            gecko_command = Write16(self.data, self.addr)
            f.write(gecko_command.as_text() + "\n")
            self.good = True
        
    def dump_info(self):
        return repr("{:s} {:08X} {:s} {:s} {:s}".format(
                    "[Immediate16]", self.addr, "-->" if self.good else "-X>", self.sym_name, self.modifier))[+1:-1]

# Paired-Singles Load and Store have a 12-bit immediate field, unlike normal load/store instructions
class Immediate12Hook(Hook):
    def __init__(self, addr, w, i, sym_name, modifier):
        Hook.__init__(self, addr)
        self.w = w
        self.i = i
        self.sym_name = sym_name
        self.modifier = modifier
    
    def resolve(self, symbols):
        # I wrote these fancy @h, @l, @ha functions to barely use them, lol.  When writing
        # 16-bit immediates, you don't really need to worry about whether or not it is
        # signed, since you're masking off any sign extension that happens regardless.
        if self.sym_name in symbols:
            if self.modifier == "@h":
                self.data = hi(symbols[self.sym_name]['st_value'], True)
            elif self.modifier == "@l":
                self.data = lo(symbols[self.sym_name]['st_value'], True)
            elif self.modifier == "@ha":
                self.data = hia(symbols[self.sym_name]['st_value'], True)
            elif self.modifier == "@sda":
                if symbols["_SDA_BASE_"]['st_value'] == None:
                    raise RuntimeError("You must set this project's sda_base member before using the @sda modifier!  Check out the set_sda_bases method.")
                self.data = mask_field(symbols[self.sym_name]['st_value'] - symbols["_SDA_BASE_"]['st_value'], 16, True)
            elif self.modifier == "@sda2":
                if symbols["_SDA2_BASE_"]['st_value'] == None:
                    raise RuntimeError("You must set this project's sda2_base member before using the @sda2 modifier!  Check out the set_sda_bases method.")
                self.data = mask_field(symbols[self.sym_name]['st_value'] - symbols["_SDA2_BASE_"]['st_value'], 16, True)
            else:
                print("Unknown modifier: \"{}\"".format(self.modifier))
            self.data = mask_field(self.data, 12, True)
            self.data |= (mask_field(self.i, 1, False) << 12)
            self.data |= (mask_field(self.w, 3, False) << 13)
    
    def apply_dol(self, dol):
        if self.data and dol.is_mapped(self.addr):
            dol.write_uint16(self.addr, self.data)
            self.good = True
    
    def write_geckocommand(self, f):
        if self.data:
            gecko_command = Write16(self.data, self.addr)
            f.write(gecko_command.as_text() + "\n")
            self.good = True
        
    def dump_info(self):
        return repr("{:s} {:08X} {:s} {:s} {:s}".format(
                    "[Immediate12]", self.addr, "-->" if self.good else "-X>", self.sym_name, self.modifier))[+1:-1]

def find_rom_end(dol):
    rom_end = 0x80000000
    for section in dol.sections:
        if section.address + section.size > rom_end:
            rom_end = section.address + section.size
    return rom_end

def try_remove(filepath):
    try:
        os.remove(filepath)
        return True
    except FileNotFoundError:
        return False

SupportedGeckoCodetypes = [
    GeckoCommand.Type.WRITE_8,
    GeckoCommand.Type.WRITE_16,
    GeckoCommand.Type.WRITE_32,
    GeckoCommand.Type.WRITE_STR,
    GeckoCommand.Type.WRITE_SERIAL,
    GeckoCommand.Type.WRITE_BRANCH,
    GeckoCommand.Type.ASM_INSERT,
    GeckoCommand.Type.ASM_INSERT_XOR,
]

class Project(object):
    def __init__(self, base_addr=None, verbose=False):
        self.base_addr = base_addr
        self.sda_base = None
        self.sda2_base = None
        
        # System member variables
        if platform.system() == "Windows":
            self.devkitppc_path = "C:/devkitPro/devkitPPC/bin/"
        else:
            self.devkitppc_path = "/opt/devkitpro/devkitPPC/bin/"
        
        # Compiling member variables
        self.src_dir = ""
        self.obj_dir = ""
        self.project_name = "project"
        self.c_files = []
        self.cpp_files = []
        self.asm_files = []
        self.obj_files = []
        self.linker_script_files = []
        self.c_flags = ["-w", "-std=c99", "-O1", "-fno-asynchronous-unwind-tables",]
        self.cpp_flags = ["-w", "-std=c++98", "-O1", "-fno-asynchronous-unwind-tables", "-fno-rtti",]
        self.asm_flags = ["-w",]
        self.linker_flags = []
        self.symbols = {}
        self.verbose = verbose
        
        # Patches member variables
        self.hooks = []
        self.gecko_codetable = GeckoCodeTable(gameName=self.project_name)
        self.gecko_code_metadata = []
        self.osarena_patcher = None
        
        # For one-time messages
        self.message_flags = [0,0,0,0,0,0,0,0,0,0,0,0]
    
    # Add stuff
    
    def add_c_file(self, filepath, flags=(), use_global_flags=True):
        self.c_files.append((filepath, flags, use_global_flags))
        
    def add_cpp_file(self, filepath, flags=(), use_global_flags=True):
        self.cpp_files.append((filepath, flags, use_global_flags))
        
    def add_asm_file(self, filepath, flags=(), use_global_flags=True):
        self.asm_files.append((filepath, flags, use_global_flags))
    
    def add_obj_file(self, filepath, do_cleanup=False):
        self.obj_files.append((filepath, do_cleanup))
    
    def add_linker_script_file(self, filepath):
        self.linker_script_files.append(filepath)
    
    def add_gecko_txt_file(self, filepath):
        with open(filepath, "r") as f:
            gecko_codetable = GeckoCodeTable.from_text(f)
        for gecko_code in gecko_codetable:
            self.gecko_codetable.add_child(gecko_code)
    
    def add_gecko_gct_file(self, filepath):
        with open(filepath, "rb") as f:
            code_table = GeckoCodeTable.from_bytes(f)
        self.gecko_codetable.append(code_table)
    
    # Hook stuff
    
    def hook_branch(self, addr, sym_name, LK=False):
        self.hooks.append(BranchHook(addr, sym_name, LK))
    
    def hook_branchlink(self, addr, sym_name):
        self.hook_branch(addr, sym_name, LK=True)
    
    def hook_pointer(self, addr, sym_name):
        self.hooks.append(PointerHook(addr, sym_name))
    
    def hook_string(self, addr, string, encoding = "ascii", max_strlen = None):
        self.hooks.append(StringHook(addr, string, encoding, max_strlen))
    
    def hook_file(self, addr, filepath, start = 0, end = None, max_size = None):
        self.hooks.append(FileHook(addr, filepath, start, end, max_size))
    
    def hook_immediate16(self, addr, sym_name, modifier):
        self.hooks.append(Immediate16Hook(addr, sym_name, modifier))
    
    def hook_immediate12(self, addr, w, i, sym_name, modifier):
        self.hooks.append(Immediate12Hook(addr, w, i, sym_name, modifier))
    
    # Set stuff
    
    def set_osarena_patcher(self, function):
        self.osarena_patcher = function
    
    def set_sda_bases(self, sda_base, sda2_base):
        self.sda_base = sda_base
        self.sda2_base = sda2_base
    
    # Do stuff
    
    def build_dol(self, in_dol_path, out_dol_path):
        with open(in_dol_path, "rb") as f:
            dol = DolFile(f)
        
        if self.base_addr == None:
            self.base_addr = (find_rom_end(dol) + 31) & 0xFFFFFFE0
            print("Base address auto-set from ROM end: {0:X}\n"
                  "Do not rely on this feature if your DOL uses .sbss2\n".format(self.base_addr))
        
        if self.base_addr % 32:
            print("WARNING!  DOL sections must be 32-byte aligned for OSResetSystem to work properly!\n")
        
        datablob = bytearray()

        if self.__build_project() == True:
            with open(self.obj_dir+self.project_name+".bin", "rb") as f:
                datablob += f.read()
                while (len(datablob) % 4) != 0:
                    datablob += b'\x00'
        
        for gecko_code in self.gecko_codetable:
            status = "ENABLED" if gecko_code.is_enabled() else "DISABLED"
            if gecko_code.is_enabled() == True:
                for gecko_command in gecko_code:
                    if gecko_command.codetype not in SupportedGeckoCodetypes:
                        status = "OMITTED"
            
            print("[GeckoCode]   {:12s} ${}".format(status, gecko_code.name))
            if status == "OMITTED":
                print("Includes unsupported codetypes:")
                for gecko_command in gecko_code:
                    if gecko_command.codetype not in SupportedGeckoCodetypes:
                        print(gecko_command)
            
            vaddress = self.base_addr + len(datablob)
            geckoblob = bytearray()
            gecko_command_metadata = []
            
            for gecko_command in gecko_code:
                if gecko_command.codetype == GeckoCommand.Type.ASM_INSERT \
                or gecko_command.codetype == GeckoCommand.Type.ASM_INSERT_XOR:
                    if status == "UNUSED" \
                    or status == "OMITTED":
                        gecko_command_metadata.append((0, len(gecko_command.value), status, gecko_command))
                    else:
                        dol.seek(gecko_command._address | 0x80000000)
                        write_branch(dol, vaddress + len(geckoblob))
                        gecko_command_metadata.append((vaddress + len(geckoblob), len(gecko_command.value), status, gecko_command))
                        geckoblob += gecko_command.value[:-4]
                        geckoblob += assemble_branch(vaddress + len(geckoblob), gecko_command._address + 4 | 0x80000000)
            datablob += geckoblob
            if gecko_command_metadata:
                self.gecko_code_metadata.append((vaddress, len(geckoblob), status, gecko_code, gecko_command_metadata))
        self.gecko_codetable.apply(dol)
        
        for hook in self.hooks:
            hook.resolve(self.symbols)
            hook.apply_dol(dol)
            if self.verbose:
                print(hook.dump_info())
        
        if len(datablob) > 0:
            new_section: Section
            if len(dol.textSections) <= DolFile.MaxTextSections:
                new_section = TextSection(self.base_addr, datablob)
            elif len(dol.dataSections) <= DolFile.MaxDataSections:
                new_section = DataSection(self.base_addr, datablob)
            else:
                raise RuntimeError("DOL is full!  Cannot allocate any new sections.")
            dol.append_section(new_section)
            
            if self.osarena_patcher:
                self.osarena_patcher(dol, self.base_addr + len(datablob))
        
        with open(out_dol_path, "wb") as f:
            dol.save(f)
    
    def build_gecko(self, gecko_path):
        with open(gecko_path, "w") as f:
            datablob = bytearray()
            
            if self.__build_project() == True:
                with open(self.obj_dir+self.project_name+".bin", "rb") as bin:
                    datablob += bin.read()
            
            f.write("[Gecko]\n")
            # Everything gets shoved into a large Gecko Code named after the project
            f.write("${}\n".format(self.project_name))
            # Copy existing Gecko Codes
            for gecko_code in self.gecko_codetable:
                if gecko_code.is_enabled():
                    f.write("* {}\n".format(gecko_code.name))
                    f.write("{}\n".format(gecko_code.as_text()))
                print("[GeckoCode]   {:12s} ${}".format("ENABLED" if gecko_code.is_enabled() else "DISABLED", gecko_code.name))
            # Create Program Data megacode
            if datablob:
                gecko_command = WriteString(datablob, self.base_addr)
                f.write("* Program Data\n")
                f.write(gecko_command.as_text() + "\n")
            # Create Hooks
            f.write("* Hooks\n")
            for hook in self.hooks:
                hook.resolve(self.symbols)
                hook.write_geckocommand(f)
                if self.verbose:
                    print(hook.dump_info())
    
    def save_map(self, map_path):
        with open(map_path, "w") as map:
            try:
                with open(self.obj_dir+self.project_name+".o", 'rb') as f:
                    elf = ELFFile(f)
                    symtab = elf.get_section_by_name(".symtab")
                    new_symbols = []
                    
                    for iter in symtab.iter_symbols():
                        # Filter out worthless symbols, as well as STT_SECTION and STT_FILE type symbols.
                        if iter.entry['st_info']['bind'] == "STB_LOCAL":
                            continue
                        # Symbols defined by the linker script have no section index, and are instead absolute.
                        # Symbols we already have aren't needed in the new symbol map, so they are filtered out.
                        if (iter.entry['st_shndx'] == 'SHN_ABS') or (iter.entry['st_shndx'] == 'SHN_UNDEF'):
                            continue
                        new_symbols.append(iter)
                    new_symbols.sort(key = lambda i: i.entry['st_value'])
                    
                    curr_section_name = ""
                    for iter in new_symbols:
                        parent_section = elf.get_section(iter.entry['st_shndx'])
                        if curr_section_name != parent_section.name:
                            curr_section_name = parent_section.name
                            map.write(
                                "\n"
                                "{} section layout\n"
                                "  Starting        Virtual\n"
                                "  address  Size   address\n"
                                "  -----------------------\n".format(curr_section_name))
                        map.write("  {:08X} {:06X} {:08X}  0 {}\n".format(
                            iter.entry['st_value'] - self.base_addr, iter.entry['st_size'], iter.entry['st_value'], iter.name))
            except OSError:
                pass
            # Record Geckoblobs from patched-in C2/F2 codetypes.  I really wanted to name this section .gecko in the
            # symbol map, but only .init and .text section headers tell Dolphin to color the symbols by index.
            if self.gecko_code_metadata:
                map.write(
                    "\n"
                    ".text section layout\n"
                    "  Starting        Virtual\n"
                    "  address  Size   address\n"
                    "  -----------------------\n")
                for code_vaddr, code_size, code_status, gecko_code, gecko_command_metadata in self.gecko_code_metadata:
                    i = 0
                    for cmd_vaddr, cmd_size, cmd_status, gecko_command in gecko_command_metadata:
                        if gecko_command.codetype == GeckoCommand.Type.ASM_INSERT \
                        or gecko_command.codetype == GeckoCommand.Type.ASM_INSERT_XOR:
                            if cmd_status == "OMITTED":
                                map.write("  UNUSED   {:06X} ........ {}${}\n".format(
                                    cmd_size, gecko_code.name, i))
                            else:
                                map.write("  {:08X} {:06X} {:08X}  0 {}${}\n".format(
                                    cmd_vaddr - self.base_addr, cmd_size, cmd_vaddr, gecko_code.name, i))
                        i += 1
            # For whatever reason, the final valid symbol loaded by Dolphin ( <= 5.0-13603 ) gets messed up
            # and loses its size.  To compensate, an dummy symbol is thrown into the map at a dubious address.
            map.write(
                "\n"
                ".dummy section layout\n"
                "  Starting        Virtual\n"
                "  address  Size   address\n"
                "  -----------------------\n"
                "  00000000 000000 81200000  0 Workaround for Dolphin's bad symbol map loader\n")
    
    def cleanup(self):
        for filename, do_cleanup in self.obj_files:
            if do_cleanup:
                try_remove(self.obj_dir+filename)
        try_remove(self.obj_dir+self.project_name+".o")
        try_remove(self.obj_dir+self.project_name+".bin")
        try_remove(self.obj_dir+self.project_name+".map")
        self.obj_files.clear()
        self.symbols.clear()
        self.gecko_code_metadata.clear()
    
    # Private stuff
    
    def __compile(self, infile, flags, use_global_flags):
        args = [self.devkitppc_path+"powerpc-eabi-gcc", "-c", self.src_dir+infile, "-o", self.obj_dir+infile+".o", "-I", self.src_dir]
        if use_global_flags:
            for flag in self.c_flags:
                args.append(flag)
        for flag in flags:
            args.append(flag)
        if self.verbose:
            print(args)
        subprocess.call(args)
        self.obj_files.append((infile+".o", True))
        return True
    
    def __compileplusplus(self, infile, flags, use_global_flags):
        args = [self.devkitppc_path+"powerpc-eabi-g++", "-c", self.src_dir+infile, "-o", self.obj_dir+infile+".o", "-I", self.src_dir]
        if use_global_flags:
            for flag in self.cpp_flags:
                args.append(flag)
        for flag in flags:
            args.append(flag)
        if self.verbose:
            print(args)
        subprocess.call(args)
        self.obj_files.append((infile+".o", True))
        return True
    
    def __assemble(self, infile, flags, use_global_flags):
        args = [self.devkitppc_path+"powerpc-eabi-as", self.src_dir+infile, "-o", self.obj_dir+infile+".o", "-I", self.src_dir]
        if use_global_flags:
            for flag in self.asm_flags:
                args.append(flag)
        for flag in flags:
            args.append(flag)
        if self.verbose:
            print(args)
        subprocess.call(args)
        self.obj_files.append((infile+".o", True))
        return True
    
    def __link_project(self):
        if self.base_addr == None:
            raise RuntimeError("Base address not set!  New code cannot be linked.")
        
        args = [self.devkitppc_path+"powerpc-eabi-ld", "-o", self.obj_dir+self.project_name+".o"]
        # The symbol "." represents the location counter.  By setting it this way,
        # we don't need a linker script to set the base address of our new code.
        args.extend(("--defsym", ".="+hex(self.base_addr)))
        # Since we have to gather sda/sda2 base addresses for the project, we
        # might as well send that info to the linker if we have it.
        if self.sda_base:
            args.extend(("--defsym", "_SDA_BASE_="+hex(self.sda_base)))
        if self.sda2_base:
            args.extend(("--defsym", "_SDA2_BASE_="+hex(self.sda2_base)))
        for file in self.linker_script_files:
            args.extend(("-T", file))
        for filename, do_cleanup in self.obj_files:
            args.append(self.obj_dir+filename)
        args.extend(("-Map", self.obj_dir+self.project_name+".map"))
        for flag in self.linker_flags:
            args.append(flag)
        if self.verbose:
            print(args)
        subprocess.call(args)
        return True
    
    def __process_project(self):
        with open(self.obj_dir+self.project_name+".o", 'rb') as f:
            elf = ELFFile(f)
            with open(self.obj_dir+self.project_name+".bin", "wb") as bin:
                for iter in elf.iter_sections():
                    # Filter out sections without SHF_ALLOC attribute
                    if iter.header["sh_flags"] & 0x2:
                        bin.seek(iter.header["sh_addr"] - self.base_addr)
                        bin.write(iter.data())
            
            symtab = elf.get_section_by_name(".symtab")
            for iter in symtab.iter_symbols():
                #print("{}   {}".format(iter.name, iter.entry))
                # Filter out worthless symbols, as well as STT_SECTION and STT_FILE type symbols.
                if iter.entry['st_info']['bind'] == "STB_LOCAL":
                    #print("{}   {}".format(iter.name, iter.entry))
                    continue
                self.symbols[iter.name] = iter.entry
            # Force _SDA_BASE_ and _SDA2_BASE_ to exist.  The compiler doesn't reliably make them available.
            self.symbols["_SDA_BASE_"] = {'st_name': 0, 'st_value': self.sda_base, 'st_size': 0, 'st_info': {'bind': 'STB_LOCAL', 'type': 'STT_OBJECT'}, 'st_other': {'visibility': 'STV_DEFAULT'}, 'st_shndx': 'SHN_ABS'}
            self.symbols["_SDA2_BASE_"] = {'st_name': 0, 'st_value': self.sda2_base, 'st_size': 0, 'st_info': {'bind': 'STB_LOCAL', 'type': 'STT_OBJECT'}, 'st_other': {'visibility': 'STV_DEFAULT'}, 'st_shndx': 'SHN_ABS'}
        return True
    
    def __build_project(self):
        os.makedirs("./" + self.src_dir, exist_ok=True)
        os.makedirs("./" + self.obj_dir, exist_ok=True)
        is_built = False
        is_linked = False
        is_processed = False
        
        for filepath, flags, use_global_flags in self.c_files:
            is_built |= self.__compile(filepath, flags, use_global_flags)
        
        for filepath, flags, use_global_flags in self.cpp_files:
            is_built |= self.__compileplusplus(filepath, flags, use_global_flags)
        
        for filepath, flags, use_global_flags in self.asm_files:
            is_built |= self.__assemble(filepath, flags, use_global_flags)
        
        if is_built == True:
            is_linked |= self.__link_project()
        if is_linked == True:
            is_processed |= self.__process_project()
        
        return is_processed
    
    # Deprecated stuff
    
    def add_branch(self, addr, sym_name, LK=False):
        if not self.message_flags[6]:
            print("\"add_branch\" is a deprecated method.  Please use \"hook_branch\" instead.")
            self.message_flags[6] = True
        self.hook_branch(addr, sym_name, LK)
    
    def add_branchlink(self, addr, sym_name):
        if not self.message_flags[7]:
            print("\"add_branchlink\" is a deprecated method.  Please use \"hook_branchlink\" instead.")
            self.message_flags[7] = True
        self.hook_branchlink(addr, sym_name)
    
    def add_pointer(self, addr, sym_name):
        if not self.message_flags[8]:
            print("\"add_pointer\" is a deprecated method.  Please use \"hook_pointer\" instead.")
            self.message_flags[8] = True
        self.hook_pointer(addr, sym_name)
    
    def add_string(self, addr, string, encoding = "ascii", max_strlen = -1):
        if not self.message_flags[9]:
            print("\"add_string\" is a deprecated method.  Please use \"hook_string\" instead.")
            self.message_flags[9] = True
        self.hook_string(addr, string, encoding, max_strlen)
    
    def add_immediate16(self, addr, sym_name, modifier):
        if not self.message_flags[10]:
            print("\"add_immediate16\" is a deprecated method.  Please use \"hook_immediate16\" instead.")
            self.message_flags[10] = True
        self.hook_immediate16(addr, sym_name, modifier)
    
    def add_immediate12(self, addr, w, i, sym_name, modifier):
        if not self.message_flags[11]:
            print("\"add_immediate12\" is a deprecated method.  Please use \"hook_immediate12\" instead.")
            self.message_flags[11] = True
        self.hook_immediate12(addr, w, i, sym_name, modifier)
    
    # VERY deprecated stuff (from Yoshi2's GC C-Kit)
    
    def add_file(self, filepath):
        if not self.message_flags[0]:
            print("\"add_file\" is a deprecated method.  Please use \"add_c_file\" instead.")
            self.message_flags[0] = True
        self.add_c_file(filepath)
    
    def add_linker_file(self, filepath):
        if not self.message_flags[1]:
            print("\"add_linker_file\" is a deprecated method.  Please use \"add_linker_script_file\" instead.")
            self.message_flags[1] = True
        self.add_linker_script_file(filepath)
    
    def branchlink(self, addr, funcname):
        if not self.message_flags[2]:
            print("\"branchlink\" is a deprecated method.  Please use \"hook_branchlink\" instead")
            self.message_flags[2] = True
        self.hook_branchlink(addr, funcname)
    
    def branch(self, addr, funcname):
        if not self.message_flags[3]:
            print("\"branch\" is a deprecated method.  Please use \"hook_branch\" instead")
            self.message_flags[3] = True
        self.hook_branch(addr, funcname)
        
    def apply_gecko(self, geckopath):
        if not self.message_flags[4]:
            print("\"apply_gecko\" is a deprecated method.  Please use \"add_gecko_txt_file\" instead.")
            self.message_flags[4] = True
        self.add_gecko_txt_file(geckopath)
    
    def build(self, newdolpath, address=None, offset=None):
        if not self.message_flags[5]:
            print("\"build\" is a deprecated method.  Please use \"build_dol\" instead.  Unfortunately, this method has no suitable redirect, so nothing can been done.")
            self.message_flags[5] = True
