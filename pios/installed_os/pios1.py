import denver
import os
import json
import secrets
import base64
import socket
import sys
from time import sleep
import shlex
import re
import subprocess
import traceback
import glob

root = ''

es = denver.ctext.ColoredText.escape

print = denver.ctext.print
input = denver.ctext.input

original_stdout = sys.stdout
original_stderr = sys.stderr
original_stdin = sys.stdin

with open( "system/_installer.u256", "r+b" ) as file_i_sha:
    sha256_installer = file_i_sha.read()


class PiosShutdown( Exception ):
    pass


class PiosReboot( Exception ):
    pass


class AutoUi:
    def __init__(self, ui: dict, command):
        self.ui = ui
        self.command = command
        self.ui_path = []

    def start_interface(self):
        while True:
            current_dir = self.get()
            sub_dirs = []
            actions = []
            for k, v in current_dir.items():
                if isinstance( v, dict ):
                    sub_dirs.append( k )
                elif isinstance( v, str ):
                    actions.append( k )
            sub_dirs.sort()
            actions.sort()
            if len( self.ui_path ) > 0:
                print( ", .." )
            index = 0
            for index, name in zip( range( len( sub_dirs ) ), sub_dirs ):
                print( ",{} {}".format( index, name ) )
            last_index = index + 1
            for index, name in zip( range( last_index, len( actions ) + last_index + 1 ), actions ):
                print( ".{} {}".format( index, name ) )
            user_input = input( "->", fore="magenta" )
            if user_input == ".." and len( self.ui_path ) > 0:
                self.ui_path.pop( -1 )
            elif user_input.isnumeric():
                if int( user_input ) in range( 0, last_index ):
                    self.ui_path.append( sub_dirs[int( user_input )] )
                elif int( user_input ) in range( last_index, index + 1 ):
                    self.command( current_dir[actions[last_index - int( user_input )]] )
            clear()

    def get(self):
        current_object = self.ui
        for sub_path in self.ui_path:
            current_object = current_object[sub_path]
        return current_object


def clear():
    pass
    # if os.name == "nt":
    #     os.system("cls")
    # else:
    #     os.system("clear")


def install_app(file_name):
    print()


def redirect_io_to_socket(s: socket.socket):
    file = s.makefile( "w", buffering=None )
    sys.stdout = file
    sys.stderr = file
    sys.stdin = s.makefile( "r", buffering=None )


def redirect_io_to_console():
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    sys.stdin = original_stdin


def make_directory_if_not_present(directory):
    if not os.path.isdir( directory ):
        os.mkdir( directory )


def make_file_if_not_present(file, data):
    if not os.path.isfile( file ):
        with open( file, "w" if isinstance( data, str ) else "w+b" ) as fp:
            fp.write( data )


def generate_default_directories_and_files():
    default_settings = {
        "remote": {
            "enabled": False,
            "host-ipv4": "127.0.0.1",
            "host-port": 3700,
            "join-password": base64.encodebytes( secrets.token_bytes( 4 ) ).decode()
        },
        "security": {
            "installation": {
                "allow-unofficial-installer": False
            }
        },
        "developer-options": {
            "enabled": False,
            "generate-log": True
        },
        "system":
            {
                "user-interface": "auto-ui",
            }
    }
    make_directory_if_not_present( "home" )
    make_directory_if_not_present( "user" )
    make_directory_if_not_present( "user/programs" )
    make_directory_if_not_present( "system" )
    make_directory_if_not_present( "user/bin" )
    if not os.path.isfile( "system/settings.json" ):
        with open( "system/settings.json", "w" ) as file:
            json.dump( default_settings, file, indent=4, sort_keys=True )


def read_file_str(file_name):
    with open( file_name ) as file:
        return file.read()


def read_file_bytes(file_name):
    with open( file_name, "w+b" ) as file:
        return file.read()


def write_file(file, data):
    with open( file, "w" if isinstance( data, str ) else "w+b" ) as fp:
        fp.write( data )


def discover_modules(path):
    modules = []
    for directory in path:
        if os.path.isdir( directory ):
            modules.extend( glob.glob( f"{directory}/*.py" ) )
            modules.extend( glob.glob( f"{directory}/*.pyc" ) )
            modules.extend( glob.glob( f"{directory}/*.pyw" ) )
            modules.extend( glob.glob( f"{directory}/*.pyo" ) )


def start_ui(ui_type):
    terminal_version = "1.0.0"
    if ui_type == "auto-ui":
        ui = {
            "Power": {
                "Shut Down": "raise PiosShutdown",
                "Reboot": "raise PiosReboot"
            },
            "Terminal": "start_ui('terminal')"
        }
        clear()
        ui = AutoUi( ui, execute_command )
        ui.start_interface()
    elif ui_type == "terminal":
        env = os.listdir( f"{root}/system/env/" )
        environment_variables = {k: read_file_str( f"{root}/system/env/{k}" ) for k in env}
        pi_path = environment_variables["PATH"].split( ';' )
        os.chdir( root )

        clear()
        # noinspection PyCallByClass
        print( denver.ctext.ColoredText.escape( "Copyright (c) 2020 xcodz." ) )
        # noinspection PyCallByClass
        print( denver.ctext.ColoredText.escape( f"{{fore_blue}}PiTerminal {{fore_green}}[{terminal_version}]" ) )
        terminal_running = True
        while terminal_running:
            user_command = input( es( os.getcwd().replace( os.sep, "/" ) + "{fore_magenta}$ " ) )
            command = shlex.split( user_command, True )
            new_command = []
            for x in command:
                s = list( x )
                while match := re.match( r"(\${(\w*?)})", ''.join( s ) ):  # Regex Expression to match this syntax
                    variable_value = match.group( 1 )  # ${VARIABLE_NAME}
                    try:
                        variable_value = environment_variables[match.group( 2 )]
                    finally:
                        s[match.start(): match.end()] = variable_value
                new_command.append( ''.join( s ) )
            # noinspection PyBroadException
            try:
                if len( new_command ) == 0:
                    continue
                elif new_command[0] == "exit":
                    terminal_running = False
                elif new_command[0] == "setenv":
                    with open( f"{root}/system/env/{new_command[1]}" ) as file:
                        file.write( new_command[2] )
                elif new_command[0] == "refresh":
                    env = os.listdir( f"{root}/system/env/" )
                    environment_variables = {k: read_file_str( f"{root}/system/env/{k}" ) for k in env}
                    pi_path = environment_variables["PATH"].split( ";" )
                elif new_command[0] == "cd":
                    os.chdir( new_command[1] )
                elif new_command[0] == "delenv":
                    os.remove( f"{root}/system/env/{new_command[1]}" )
                elif new_command[0] == "echo":
                    print( new_command[1] )
                elif new_command[0] == "pecho":
                    print( *new_command[1].split( ";" ), sep="\n" )
                elif new_command[0] == "dlp":
                    print()
                elif new_command[0] == "help":
                    print( """
Builtin Commands:
    setenv name value                Set an environment variable
    help                             See this help message
    exit                             Exit current session
    refresh                          Refresh current environment
    cd path                          Change directory
    delenv name                      Delete an environment variable
    echo value                       Print a value
    pecho value                      Print a value split at ';' 
    dlp url                          Download a package and install""" )
            except:
                error_msg = traceback.format_exc()
                print( error_msg )
            finally:
                print()


def execute_script(arguments: list):
    return subprocess.run( arguments, stderr=sys.stderr, stdout=sys.stdout, stdin=sys.stdin )


def execute_command(statement):
    exec( statement, globals() )


def start_os():
    clear()
    print( "Booting PiOS", fore="green" )
    generate_default_directories_and_files()
    print( "Welcome" )
    sleep( 1 )
    clear()

    settings = json.loads( read_file_str( "system/settings.json" ) )

    start_ui( settings["system"]["user-interface"] )


def main():
    global root
    root = os.getcwd()
    pios_running = True
    while pios_running:
        try:
            start_os()
            pios_running = False
        except PiosShutdown:
            clear()
            print( "Shutting Down", fore="red" )
            pios_running = False
        except PiosReboot:
            clear()
            print( "Rebooting", fore="red" )
        except KeyboardInterrupt:
            clear()
            print( "Forced Rebooting", fore="red" )
        except Exception as e:
            clear()
            print( f"{repr( e )} [rebooting]", fore="red" )
            sleep( 2 )
        sleep( 1 )
        clear()
        os.chdir( root )
