#!/bin/env perl

use warnings;
use strict;
use File::Basename;

# 1) Edit the following line to reflect the location of the OVR include files on your system
my $include_folder = "C:/Users/brunsc/Documents/ovr_sdk_win_0.7.0.0/OculusSDK/LibOVR/Include";

# 2) Edit this list to change the set of header files to translate
my @header_files = (
    "OVR_ErrorCode.h",
    "OVR_CAPI_0_7_0.h",
    "OVR_CAPI_GL.h",
    "Extras/OVR_CAPI_Util.h",
);

# No more modifications should be necessary...

my $type_rx = '\S[^;\n()]*\S+'; # can have spaces, e.g. "const unsigned int"
my $ident_rx = '[a-zA-Z0-9_]+'; # yes, initial underscores should be parsed too...
my $comment_line_rx = '(?<=\n)[\ ]*(?://|/\*)[^\n]*\n';

translate_header();


sub translate_header {
    open my $fh, ">", "translated.py" or die;

    print $fh <<'END_PREAMBLE';
"""
Python module "ovr"
Python bindings for Oculus Rift SDK version 0.7.0

Works on Windows only at the moment (just like Oculus Rift SDK...)
"""

import ctypes
from ctypes import byref
import sys
import textwrap
import math
import platform


OVR_PTR_SIZE = ctypes.sizeof(ctypes.c_voidp) # distinguish 32 vs 64 bit python

# Load Oculus runtime library (only tested on Windows)
# 1) Figure out name of library to load
_libname = "OVRRT32_0_7" # 32-bit python
if OVR_PTR_SIZE == 8:
    _libname = OVRRT64_0_7 # 64-bit python
if platform.system().startswith("Win"):
    _libname = "Lib"+_libname # i.e. "LibOVRRT32_0_7"
# Load library
try:
    libovr = ctypes.CDLL(_libname)
except:
    print "Is Oculus Runtime 0.7 installed on this machine?"
    raise


ENUM_TYPE = ctypes.c_int32 # Hopefully a close enough guess...


class HmdStruct(ctypes.Structure):
    "Used as an opaque pointer to an OVR session."
    pass


END_PREAMBLE

    process_headers($fh);

    print $fh <<'END_FOOTER';
# Run test program
if __name__ == "__main__":
    # Transcribed from initial example at 
    # https://developer.oculus.com/documentation/pcsdk/latest/concepts/dg-sensor/
    initialize(None)
    hmd, luid = create()
    desc = getHmdDesc(hmd)
    print desc.Resolution
    print desc.ProductName
    # Start the sensor which provides the Rift's pose and motion.
    configureTracking(hmd, 
        TrackingCap_Orientation | # requested capabilities
        TrackingCap_MagYawCorrection |
        TrackingCap_Position, 
        0) # required capabilities
    # Query the HMD for the current tracking state.
    ts  = getTrackingState(hmd, getTimeInSeconds())
    if ts.StatusFlags & (Status_OrientationTracked | Status_PositionTracked):
        pose = ts.HeadPose
        print pose.ThePose
        # TODO:

    destroy(hmd)
    shutdown()
END_FOOTER

    close $fh;
}

sub process_headers {
    my $fh = shift;
    foreach my $inc (@header_files) {
        my $h = join("/", $include_folder, $inc);
        process_header($h, $fh);
    }
}

sub process_header {
    my $header = shift;
    my $out = shift;
    print "Processing $header...\n";
    die "ERROR: $header does not exist\n" unless -e $header;

    my $short_header_name = basename($header);

    print $out "### BEGIN Declarations from C header file $short_header_name ###\n\n\n";

    # TODO:
    my $header_string = do {
        local $/ = undef;
        open my $fhh, "<", $header
            or die "could not open $header: $!";
        <$fhh>;
    };
    # print length $header_string, " characters read\n";

    process_code_block($header_string, $out, $short_header_name);

    print $out "### END Declarations from C header file $short_header_name ###\n\n\n";    
}

sub process_code_block {
    my $code = shift;
    my $out = shift;
    my $fname = shift;

    # Store offsets of code lines, so we can later translate positions to line numbers
    my @line_for_pos = ();
    push @line_for_pos, 1;
    my $line_count = 0;
    while ($code =~ m/(\n)/g) {
        push @line_for_pos, pos($code) + 1;
        $line_count += 1;
    }
    # print "$line_count lines found\n";

    my %translated_by_pos = ();

    process_simple_typedefs($code, \%translated_by_pos);
    process_enums($code, \%translated_by_pos);
    process_macros($code, \%translated_by_pos);

    my $line_number = 0;
    foreach my $pos (sort {$a <=> $b} keys %translated_by_pos) {
        while ($line_for_pos[$line_number] < $pos) {
            $line_number += 1;
        }
        print $out "# Translated from header file $fname line $line_number\n";
        print $out $translated_by_pos{$pos}, "\n\n";
    }
}

sub process_macros {
    my $code = shift;
    my $by_pos = shift;

    # First use a simple regex, to be sure of counting all examples
    # e.g. "#define OVR_SUCCESS(result) (result >= 0)"
    my $count1 = 0;
    # Look for typedefs with a semicolon on the same line
    while ($code =~ m/
            \#define\s+
            ([^( ]+) # function name
            \( # open paren
            ([^)]+) # arguments
            \) # close paren
            \s*
            \( # open paren
            ([^\n]+) # arguments
            \) # close paren            
            /gx) 
    {
        my $fn_name = $1;
        my $args = $2;
        my $fn_body = $3;
        my $p = pos($code);

        # Remove OVR_ prefix
        $fn_name =~ s/\bOVR_//g;
        $fn_body =~ s/\bOVR_//g;

        # Translate not
        $fn_body =~ s/!/not /g;

        my $trans = "def $fn_name($args):\n    return $fn_body\n";

        $by_pos->{$p} = $trans;
        $count1 += 1;
    }

    print $count1, " macros found\n";

}

sub process_enums {
    my $code = shift;
    my $by_pos = shift;

    # First use a simple regex, to be sure of counting all examples
    # "typedef int32_t ovrResult;"
    my $count1 = 0;
    # Look for typedefs with a semicolon on the same line
    while ($code =~ m/\n[ \t]*typedef\s+enum\s+/g) {
        $count1 += 1;
    }

    my $count2 = 0;

    while ($code =~ m/
            ((?:$comment_line_rx)*) # Previous block of comment lines
            (?<=\n)[\ \t]* # lookbehind for start of line
            typedef\s+enum\s+ # 
            $ident_rx # first unused enum name
            \s*\{ # open brace
            ([^\}]*) # TODO: contents
            \}\s* # close brace
            ($ident_rx) # primary enum name
            /gx) 
    {
        my $comment = $1;
        my $contents = $2;
        my $enum_name = $3;
        my $p = pos($code);

        $comment = translate_comment($comment);

        # 1) Declare type alias for enum
        $enum_name = translate_type($enum_name);
        my $trans = "$enum_name = ENUM_TYPE\n";
        # 2) Fill in contents

        my $prev_val = "";
        foreach my $line (split "\n", $contents) {
            next if $line =~ m/^\s*$/; # skip blank lines
            $line =~ s!///!\#!; # convert comments to python style
            $line =~ s!//!\#!; # convert comments to python style
            $line =~ s!/\*!\#!; # convert comments to python style
            $line =~ s!\*/!\#!; # convert comments to python style
            $line =~ s/^\s*//; # remove leading spaces
            # Translate individual enum entries, removing comma
            # e.g. "ovrSuccess_HMDFirmwareMismatch        = 4100,   ///< The HMD Firmware is out of date but is acceptable."
            # "    ovrDebugHudStereo_EnumSize = 0x7fffffff     ///< \internal Force type int32_t"
            if ($line =~ m/^($ident_rx)(\s*\=\s*)([^, ]+)\,?(.*)$/) {
                my $id = $1;
                my $equals = $2;
                my $val = $3;
                my $rest = $4;

                $id = translate_type($id);
                $val = translate_type($val); # Might be another enum value
                $line = "$id$equals$val$rest";

                $prev_val = $id;
            }
            # Some enum components have an implicit value, so increment previous value
            # e.g. ovrDebugHudStereo_Count,                    ///< \internal Count of enumerated elements
            elsif ($line =~ m/^($ident_rx)\,?\s?(.*)$/) {
                my $id = $1;
                my $rest = $2;
                my $val = "$prev_val + 1";

                $id = translate_type($id);
                $val = translate_type($val); # Might be another enum value
                $line = "$id = $prev_val + 1 $rest";

                $prev_val = $id;
            }

            $trans .= "$line\n";
        }

        $by_pos->{$p} = $trans;
        $count2 += 1;
    }

    # print "$count1 ($count2) enums found\n";
    die unless $count1 == $count2;
}

sub process_simple_typedefs {
    my $code = shift;
    my $by_pos = shift;

    # First use a simple regex, to be sure of counting all examples
    # "typedef int32_t ovrResult;"
    my $count1 = 0;
    # Look for typedefs with a semicolon on the same line
    while ($code =~ m/(typedef[^\n\/()]*;)/g) {
        $count1 += 1;
    }

    my $count2 = 0;    
    while ($code =~ m/
            ((?:$comment_line_rx)*) # Previous block of comment lines
            (?<=\n)[ \t]* # Lookbehind for beginning of line
            typedef[ \t]+ # typedef
            ($type_rx)[ \t]+ # existing type
            ($ident_rx)[ \t]* # new type
            ; # semicolon
            ([^\n]*) # rest of line
            /gx) 
    {
        my $pre_comment = $1;
        my $type = $2;
        my $ident = $3;
        my $rest = $4;
        my $p = pos($code);

        $pre_comment = translate_comment($pre_comment);
        $rest = translate_comment($rest);

        my $tid = translate_type($ident); # Yes, translate_type, not translate_ident
        my $ttype = translate_type($type);
        my $trans = "$pre_comment$tid = $ttype $rest\n";
        # print $trans;
        $by_pos->{$p} = $trans;
        $count2 += 1;
    }

    # print "$count1 ($count2) simple typedefs found\n";
    die unless $count1 == $count2;
}

sub translate_comment {
    my $c = shift;
    $c = "" unless defined $c;

    $c =~ s!^([^/]*)///!$1\#!mg; # Convert to python style comment
    $c =~ s!^([^/]*)//!$1\#!mg; # Convert to python style comment
    $c =~ s!^([^/]*)/\*!$1\#!mg; # Convert to python style comment

    # print $c;

    return $c;
}

sub translate_ident {
    my $id0 = shift;
    # TODO
    return $id0;
}

sub translate_type {
    my $type = shift;
    # remove const
    $type =~ s/\bconst\s+//g;
    $type =~ s/\s+const\b//g;
    # remove struct
    $type =~ s/\bstruct\s+//g;
    # no implicit int
    $type = "unsigned int" if $type =~ m/^\bunsigned\b$/;
    # abbreviate type
    $type =~ s/_t\b//g; # int32_t => int32
    $type =~ s/\bunsigned\s+/u/g; # unsigned int => uint
    # translate to ctypes type name
    if ($type =~ m/^(float|u?int|double|u?char|u?short|u?long)/) {
        $type = "ctypes.c_$type";
    }
    # remove leading "ovr" or "ovr_"
    if ($type =~ m/^ovr_?(.*)$/) {
        $type = ucfirst($1); # capitalize first letter of types
    }
    # translate pointer type
    while ($type =~ m/^([^\*]+)\*(.*)$/) { # HmdStruct* -> ctypes.POINTER(HmdStruct)
       $type = "ctypes.POINTER($1)$2";
    }
    return $type;
}
