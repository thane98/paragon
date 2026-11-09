#written by ErrantSquam for Paragon use

import re


class Fe10ScriptParser:

    def __init__(self):
        
        self.bg_types = {
            "R":"Layout",
            "B":"TransitionBG",
            "b":"QuickSwapBG"
        }

        self.mouth_types = {
            "c":"Closed",
            "d":"Default",
            "o":"Open"
        }
        self.eye_types = {
            "c":"Closed",
            "h":"HalfOpen",
            "o":"Open",
            "O":"Open_UNKNOWN"
        }
        self.expression_types = {
            "a":"MouthSet2",
            "s":"MouthSet1"
        }

        #todo: json?
        self.function_dict = {
            "SuspendUntilResume": {
                "Bytecode": "1",
                "Function":"SuspendUntilResume",
                "Args": ["H"],
                },
            "ResumeSuspendedScript": {
                "Bytecode": "1",
                "Function":"ResumeSuspendedScript",
                "Args":[{
                    "ArgName":"Type",
                    "Mappings": None
                }]
                },
            "SetExpression" : {
                "Bytecode": "1",
                "Function": "SetExpression",
                "Args":[{
                    "ArgName":"State",
                    "Mappings": self.expression_types
                }]
                },
            "ClearTextBox" : {
                "Bytecode": "1",
                "Function": "ClearTextBox",
                "Args":[{"ArgName":"Type",
                    "Mappings": None
                }]
                },
            "UnknownFunction1" : {
                "Bytecode": "1",
                "Function": "UnknownFunction1",
                "Args":[{"ArgName":"arg1",
                    "Mappings": None
                }]
                },
            "DisableBSkip" : {
                "Bytecode": "2",
                "Function": "DisableBSkip",
                "Args":[{"ArgName":"arg1",
                    "Mappings": None
                },
                {
                    "ArgName":"arg2",
                    "Mappings": None
                }]
                },
            "SetEyes" : {
                "Bytecode": "2",
                "Function": "SetEyes",
                "Args":["e",
                {
                    "ArgName":"State",
                    "Mappings": self.eye_types
                }]
                },
            "SetMouth" : {
                "Bytecode": "2",
                "Function": "SetMouth",
                "Args":["m",
                {
                    "ArgName":"State",
                    "Mappings": self.mouth_types
                }]
                },
            "PauseTicks" : {
                "Bytecode": "2",
                "Function": "PauseTicks",
                "Args":["w",
                {
                    "ArgName":"Time",
                    "Mappings": None
                }]
                },
            "ToggleNameplateVisibility" : {
                "Bytecode": "2",
                "Function": "ToggleNameplateVisibility",
                "Args": ["n",
                "c"]
                },
            "UnknownFunction2" : {
                "Bytecode": "2",
                "Function": "UnknownFunction2",
                "Args":[{
                    "ArgName":"arg1",
                    "Mappings": None
                },
                {
                    "ArgName":"arg2",
                    "Mappings": None
                }]
                },
            "DisableBSkip_DFC" : {
                "Bytecode": "3",
                "Function": "DisableBSkip_DFC",
                "Args":["D", "F", "C"]
                },
            "UnknownFunction3" : {
                "Bytecode": "3",
                "Function": "UnknownFunction3",
                "Args":[{
                    "ArgName":"arg1",
                    "Mappings": None
                },
                {
                    "ArgName":"arg2",
                    "Mappings": None
                },
                {
                    "ArgName":"arg3",
                    "Mappings": None
                }]
                },
            "InitScene" : {
                "Bytecode": "4",
                "Function": "InitScene",
                "Args":[{
                    "ArgName":"BgType",
                    "Mappings": self.bg_types
                },
                {"ArgName": "Bg",
                    "Mappings": None
                }],
                "BonusNewline": "\n\n"
            },
            "PlayVoice" : {
                "Bytecode": "4",
                "Function": "PlayVoice",
                "Args":["V",
                {"ArgName": "VoiceChannel",
                    "Mappings": None
                }]
            },
            "PlaySound" : {
                "Bytecode": "4",
                "Function": "PlaySound",
                "Args":["S",
                {"ArgName": "SoundEffect",
                    "Mappings": None
                }]
            },
            "PauseMs" : {
                "Bytecode": "4",
                "Function": "PauseMs",
                "Args":[{
                    "ArgName":"Type",
                    "Mappings": None
                },
                {"ArgName": "Time",
                    "Mappings": None
                },]
            },
            "ScreenTransitionMs" : {
                "Bytecode": "4",
                "Function": "ScreenTransitionMs",
                "Args":["F",
                {"ArgName": "Time",
                    "Mappings": None
                },]
            },
            "UnknownFunction4" : {
                "Bytecode": "4",
                "Function": "UnknownFunction4",
                "Args":[{
                    "ArgName":"arg1",
                    "Mappings": None
                },
                {"ArgName": "arg2",
                    "Mappings": None
                }]
            },
            "AssignCast" : {
                "Bytecode": "5",
                "Function": "AssignCast",
                "Args":["FL",
                {
                    "ArgName": "Cast",
                    "Mappings": None,
                    "isArray": True
                }]
            },
            "AssignCurrentSpeaker" : {
                "Bytecode": "7",
                "Function": "AssignCurrentSpeaker",
                "Args": [
                    {
                        "ArgName":"Actor",
                        "Mappings": None
                    },
                    {
                        "ArgName":"Pos",
                        "Mappings": None
                    }
                ],
                "BonusNewline": "\n"
            },
            "CurrentSpeakerEnterAndEndTick": {
                "Bytecode": "8",
                "Function": "CurrentSpeakerEnterAndEndTick",
                "Args": [
                    {
                        "ArgName":"Pos",
                        "Mappings": None
                    },
                    {
                        "ArgName":"Dir",
                        "Mappings": None
                    }
                ],
                "BonusNewline": "\n"
            },
            "CurrentSpeakerEnter": {
                "Bytecode": "14",
                "Function": "CurrentSpeakerEnter",
                "Args": [
                    {
                        "ArgName":"Pos",
                        "Mappings": None
                    },
                    {
                        "ArgName":"Dir",
                        "Mappings": None
                    }
                ],
                "BonusNewline": "\n"
            },
            "CurrentSpeakerLeaveAndEndTick": {
                "Bytecode": "9",
                "Function": "CurrentSpeakerLeaveAndEndTick",
                "Args": [],
                "BonusNewline": "\n"
            },
            "CurrentSpeakerLeave": {
                "Bytecode": "15",
                "Function": "CurrentSpeakerLeave",
                "Args": [],
                "BonusNewline": "\n"
            },
            "SelectActorAsCurrent" : {
                "Bytecode": "12",
                "Function": "SelectActorAsCurrent",
                "Args": [
                    {
                        "ArgName":"Actor",
                        "Mappings": None
                    },
                    {
                        "ArgName":"Pos",
                        "Mappings": None
                    }
                ],
                "BonusNewline": "\n"
            },
            "NewLine" : {
                "Bytecode": "10",
                "Function": "NewLine",
                "Args": [],
            },
            "UnknownSkipNextTwoBytes" : {
                "Bytecode": "11",
                "Function": "UnknownSkipNextTwoBytes",
                "Args": [],
            },
            "Scroll" : {
                "Bytecode": "16",
                "Function": "Scroll",
                "Args": [],
                "BonusNewline": "\n"
            },
            "PressA" : {
                "Bytecode": "17",
                "Function": "PressA",
                "Args": [],
                "BonusNewline": "\n\n"
            },
            "EndTickWithoutWaiting" : {
                "Bytecode": "18",
                "Function": "EndTickWithoutWaiting",
                "Args": [],
            },

        }

        self.bytecode_to_function = {
            "1": {
                "H": self.function_dict["SuspendUntilResume"],
                "@": self.function_dict["ResumeSuspendedScript"],
                "*": self.function_dict["ResumeSuspendedScript"],
                "a": self.function_dict["SetExpression"],
                "s": self.function_dict["SetExpression"],
                "P": self.function_dict["ClearTextBox"],
                "G": self.function_dict["ClearTextBox"],
                None: self.function_dict["UnknownFunction1"]
            },
            "2": {
                "s": self.function_dict["DisableBSkip"],
                "e": self.function_dict["SetEyes"],
                "m": self.function_dict["SetMouth"],
                "w": self.function_dict["PauseTicks"],
                "n": self.function_dict["ToggleNameplateVisibility"],
                None: self.function_dict["UnknownFunction2"]
            },
            "3": {
                "D": self.function_dict["DisableBSkip_DFC"],
                None: self.function_dict["UnknownFunction3"]
            },
            "4": {
                "R": self.function_dict["InitScene"],
                "B": self.function_dict["InitScene"],
                "b": self.function_dict["InitScene"],
                "F": self.function_dict["ScreenTransitionMs"],
                "V": self.function_dict["PlayVoice"],
                "S": self.function_dict["PlaySound"],
                "W": self.function_dict["PauseMs"],
                "s": self.function_dict["PauseMs"],
                None: self.function_dict["UnknownFunction4"]
            },
            "5": {
                None: self.function_dict["AssignCast"]
            },
            "7": {
                None: self.function_dict["AssignCurrentSpeaker"]
            },
            "8": {
                None: self.function_dict["CurrentSpeakerEnterAndEndTick"]
            },
            "9": {
                None: self.function_dict["CurrentSpeakerLeaveAndEndTick"]
            },
            "10":{
                None: self.function_dict["NewLine"]
            },
            "11":{
                None: self.function_dict["UnknownSkipNextTwoBytes"]
            },
            "12": {
                None: self.function_dict["SelectActorAsCurrent"]
            },
            "14": {
                None: self.function_dict["CurrentSpeakerEnter"]
            },
            "15": {
                None: self.function_dict["CurrentSpeakerLeave"]
            },
            "16":{
                None: self.function_dict["Scroll"]
            },
            "17":{
                None: self.function_dict["PressA"]
            },
            "18": {
                None: self.function_dict["EndTickWithoutWaiting"]
            }
        }



    @staticmethod
    def regex_and_replace(capture_group, 
                          replacement_function, full_message):
        commands = re.findall(fr"({capture_group})", full_message)
        for i in commands:
            try:
                replacement = replacement_function(i)
                full_message = full_message.replace(i[0], replacement)
            finally: #In the case of unknown bytecode
                pass
        return full_message

    @staticmethod
    def get_reversed_dict(format_dict:dict) -> dict:
        return {v: k for k, v in format_dict.items()}

    def controlcode_to_bytecode(self, pretty_function:str) -> str:
        control_code = re.findall(r"\[(\w+).*?\]", pretty_function)[0]
        control_args = re.findall(r"(\w+)='(.*?)'", pretty_function)

        try:
            function_details = self.function_dict[control_code]
        except KeyError:
            return pretty_function
        
        return_value = f'$({function_details["Bytecode"]})'
        function_args_list = self.function_dict[control_code]["Args"]
        pretty_arg_index = 0

        for i, current_game_arg in enumerate(function_args_list):
            if pretty_arg_index > len(control_args):
                break
            if not isinstance(current_game_arg, dict):
                return_value += function_args_list[i]
            else:
                current_pretty_arg = control_args[pretty_arg_index][1]
                if "isArray" in function_args_list[i].keys() \
                and function_args_list[i]["isArray"]:
                    
                    current_pretty_array = current_pretty_arg.split(",")
                    current_pretty_array = [i.strip() for i in current_pretty_array]
                    return_value += "|" + "|".join(current_pretty_array) + "||"  

                elif function_args_list[i]["Mappings"] is not None:

                    reverse_mappings = self.get_reversed_dict(function_args_list[i]["Mappings"])
                    return_value += reverse_mappings[current_pretty_arg]
                else:
                    return_value += current_pretty_arg
                pretty_arg_index += 1

        if function_details["Bytecode"] == "4":
            return_value += "|"

        return return_value

    def convert_pretty_to_raw_message(self, string):

        controlCodes = re.findall(r"(\[.*?\])", string)

        for i in controlCodes:
            reconstructed_bytecode = self.controlcode_to_bytecode(i)
            string = string.replace(i, reconstructed_bytecode)

        string = string.replace("\n", "")
        string = string.replace("$(10)", "\\n")
        return string



    def bytecode_args_to_controlcode_args(self, arg_details, arg):
        if isinstance(arg_details, dict):
            if "isArray" in arg_details.keys() and arg_details["isArray"]:
                arg_array = arg.split("|")
                return f"{arg_details['ArgName']}='{', '.join(arg_array)}'"
            elif arg_details["Mappings"] != None:
                return f"{arg_details['ArgName']}='{arg_details['Mappings'][arg]}'"
            else:
                return f"{arg_details['ArgName']}='{arg}'"
        return ""

    
    def bytecode_to_controlcode(self, bytecode:str, command_args:list[str]) -> str:
        try:
            function_details = self.bytecode_to_function[str(bytecode)][command_args[1]]
        except (IndexError, KeyError) as e:
            function_details = self.bytecode_to_function[str(bytecode)][None]



        parsed_string = "[" + function_details["Function"]


        for i in range(1, len(command_args)):
            parsed_substring = self.bytecode_args_to_controlcode_args(function_details["Args"][i-1], command_args[i])
            if parsed_substring.strip() != "":
                parsed_string += " " + parsed_substring 
        parsed_string += "]"


        if "BonusNewline" in function_details.keys():
            parsed_string+= function_details["BonusNewline"]

        return parsed_string

        

    def convert_raw_message_to_pretty(self, fe10_message:str) -> str:
        fe10_message = fe10_message.replace("\\n", "[NewLine]\n")

        bytecodeCaptureGroupList = [
            (1, r"\$\(1\)(.{1})"),
            (2, r"\$\(2\)(\w{1})(\w{1})"),
            (3, r"\$\(3\)(\w{1})(\w{1})(\w{1})"),
            (4, r"\$\(4\)(\w{1})(.*?)\|"),
            (5, r"\$\(5\)(FL)\|(.*)\|\|"),
            (7, r"\$\(7\)(\d{1})(\d{1})"),
            (8, r"\$\(8\)(\d{1})(\w{1})"),
            (12,r"\$\(12\)(\d{1})(\d{1})"),
            (14, r"\$\(14\)(\d{1})(\w{1})"),
        ]

        noArgCaptureGroupList = [
            9, 10, 11, 15, 16, 17, 18 
        ]

        for bytecode_args in bytecodeCaptureGroupList:
            bytecode = bytecode_args[0]
            command_capture_group = bytecode_args[1]
            fe10_message = self.regex_and_replace(command_capture_group, 
            lambda i, bc=bytecode:self.bytecode_to_controlcode(bc, i), 
            fe10_message)

        for i in noArgCaptureGroupList:
            fe10_message = fe10_message.replace(f"$({i})", 
                                    self.bytecode_to_controlcode(i, []))

        return fe10_message
