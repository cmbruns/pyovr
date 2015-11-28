#!/bin/env perl

use warnings;
use strict;
use File::Basename;

# 1) Edit the following line to reflect the location of the OVR include files on your system
my $include_folder = "C:/Users/cmbruns/Documents/ovr_sdk_win_0.8.0.0/OculusSDK/LibOVR/Include";
# my $include_folder = "C:/Users/brunsc/Documents/ovr_sdk_win_0.8.0.0/OculusSDK/LibOVR/Include";
# my $include_folder = "C:/Program Files/ovr_sdk_win_0.8.0.0/OculusSDK/LibOVR/Include";

# 2) Edit this list to change the set of header files to translate
my @header_files = (
    "OVR_Version.h",
    "OVR_CAPI_Keys.h",
    "OVR_ErrorCode.h",
    "OVR_CAPI_0_8_0.h",
    "OVR_CAPI_GL.h",
    "Extras/OVR_CAPI_Util.h",
);

# No more modifications should be necessary...

my $type_rx = '[^;\n(),\s/][^;\n(),/]*[^;\n(),\s/]'; # can have spaces, e.g. "const unsigned int"
my $ident_rx = '[a-zA-Z0-9_]+'; # yes, initial underscores should be parsed too...
my $comment_line_rx = '(?<=\n)[\ ]*(?://|/\*)[^\n]*\n';

# Some types should act like python sequences

my @sequence_methods = (
<<"END_LEN"

    def __len__(self):
        "number of items in this container"
        return len(self._fields_)
END_LEN
,
<<"END_GETITEM"

    def __getitem__(self, key):
        "access contained elements"
        if isinstance(key, slice):
            return [self[ii] for ii in xrange(*key.indices(len(self)))]
        else:
            return getattr(self, self._fields_[key][0])
END_GETITEM
,
);

my %custom_methods = ();
# Treat some wrapped classes as containers
foreach my $seq_type ("Vector2i", "Sizei", "Vector2f", 
        "Vector2f", "Vector3f") 
{
    $custom_methods{$seq_type} = \@sequence_methods;
}

my @sequence_methods_quat = @sequence_methods; # copy array
$custom_methods{"Quatf"} = \@sequence_methods_quat;
push @{$custom_methods{"Quatf"}}, (
<<"END_EULER"

    def getEulerAngles(self, axis1=0, axis2=1, axis3=2, rotate_direction=1, handedness=1):
        assert(axis1 != axis2)
        assert(axis1 != axis3)
        assert(axis2 != axis3)
        Q = [ self.x, self.y, self.z ]  # Quaternion components x,y,z
        ww  = self.w*self.w;
        Q11 = Q[axis1]*Q[axis1]
        Q22 = Q[axis2]*Q[axis2]
        Q33 = Q[axis3]*Q[axis3]
        psign = -1.0
        # Determine whether even permutation
        if ((axis1 + 1) % 3 == axis2) and ((axis2 + 1) % 3 == axis3):
            psign = 1.0
        s2 = psign * 2.0 * (psign*self.w*Q[axis2] + Q[axis1]*Q[axis3])
        SingularityRadius = 1e-10
        D = rotate_direction # CCW rotation
        S = handedness # Right handed coordinate system
        if s2 < -1.0 + SingularityRadius:
            # South pole singularity
            a = 0.0
            b = -S*D*math.pi/2
            c = S*D*math.atan2(2.0*(psign*Q[axis1]*Q[axis2] + self.w*Q[axis3]),
                           ww + Q22 - Q11 - Q33 )
        elif s2 > 1.0 - SingularityRadius:
            # North pole singularity
            a = 0.0
            b = S*D*math.pi/2
            c = S*D*math.atan2(2.0*(psign*Q[axis1]*Q[axis2] + self.w*Q[axis3]),
                           ww + Q22 - Q11 - Q33)
        else:
            a = -S*D*math.atan2(-2.0*(self.w*Q[axis1] - psign*Q[axis2]*Q[axis3]),
                            ww + Q33 - Q11 - Q22)
            b = S*D*math.asin(s2)
            c = S*D*math.atan2(2.0*(self.w*Q[axis3] - psign*Q[axis1]*Q[axis2]),
                           ww + Q11 - Q22 - Q33)     
        return a, b, c
END_EULER
,
);

push @{$custom_methods{"Matrix4f"}}, (
<<"END_MATMETH"

    def __len__(self):
        "number of items in this container"
        return 16

    def __getitem__(self, key):
        "access contained elements as a single flat list"
        i = int(key/4)
        j = key % 4
        return self.M[j][i]
END_MATMETH
);

translate_header();


sub translate_header {
    open my $fh, ">", "translated.py" or die;

    print $fh <<'END_PREAMBLE';
"""
Python module "ovr"
Python bindings for Oculus Rift SDK version 0.8.0

Works on Windows only at the moment (just like Oculus Rift SDK...)
"""

import ctypes
from ctypes import *
import sys
import textwrap
import math
import platform


OVR_PTR_SIZE = sizeof(c_voidp) # distinguish 32 vs 64 bit python

# Load Oculus runtime library (only tested on Windows)
# 1) Figure out name of library to load
_libname = "OVRRT32_0_8" # 32-bit python
if OVR_PTR_SIZE == 8:
    _libname = "OVRRT64_0_8" # 64-bit python
if platform.system().startswith("Win"):
    _libname = "Lib"+_libname # i.e. "LibOVRRT32_0_8"
# Load library
try:
    libovr = CDLL(_libname)
except:
    print "Is Oculus Runtime 0.8 installed on this machine?"
    raise


ENUM_TYPE = c_int32 # Hopefully a close enough guess...


class HmdStruct(Structure):
    "Used as an opaque pointer to an OVR session."
    pass


# Signature of the logging callback function pointer type.
#
# \param[in] userData is an arbitrary value specified by the user of ovrInitParams.
# \param[in] level is one of the ovrLogLevel constants.
# \param[in] message is a UTF8-encoded null-terminated string.
# \see ovrInitParams ovrLogLevel, ovr_Initialize
#
# typedef void (OVR_CDECL* ovrLogCallback)(POINTER(c_uint) userData, int level, const char* message);
LogCallback = CFUNCTYPE(None, POINTER(c_uint), c_int, c_char_p)


def POINTER(obj):
    p = ctypes.POINTER(obj)

    # Convert None to a real NULL pointer to work around bugs
    # in how ctypes handles None on 64-bit platforms
    if not isinstance(p.from_param, classmethod):
        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x
        p.from_param = classmethod(from_param)

    return p


def byref(obj):
    "Referencing None should result in None, at least for initialize method"
    b = None if obj is None else ctypes.byref(obj)
    return b

ovrFalse = c_char(chr(0)) # note potential conflict with Python built in symbols
ovrTrue = c_char(chr(1))

def toOvrBool(arg):
    # One tricky case:
    if arg == chr(0):
        return ovrFalse
    # Remainder are easy cases:
    if bool(arg):
        return ovrTrue
    else:
        return ovrFalse

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
    process_structs($code, \%translated_by_pos);
    process_functions($code, \%translated_by_pos);
    process_constants($code, \%translated_by_pos);

    my $line_number = 0;
    foreach my $pos (sort {$a <=> $b} keys %translated_by_pos) {
        while ($line_for_pos[$line_number] < $pos) {
            $line_number += 1;
        }
        print $out "# Translated from header file $fname line $line_number\n";
        print $out $translated_by_pos{$pos}, "\n\n";
    }
}

sub process_constants {
    my $code = shift;
    my $by_pos = shift;

    # First use a simple regex, to be sure of counting all examples
    my $count1 = 0;
    # "OVR_PUBLIC_FUNCTION(ovrResult) ovr_Initialize(const ovrInitParams* params);"
    while ($code =~ m!(?<=\n)\#define\s+OVR_(\S+)\s+(\S+)\s*(//.*)?!g) {
        my $key = $1;
        my $value = $2;
        my $comment = $3;
        my $p = pos($code) - length($&);

        next if $key =~ m/_h$/; # OVR_CAPI_0_8_0_h
        next if $key =~ m/_DEFINED$/; # OVR_SUCCESS_DEFINED

        $value =~ s/f$//; # Remove float tag from literals
        $value =~ s/\{/\[/g;
        $value =~ s/\}/\]/g;
        $value =~ s/OVR_//; # equal to other key...

        $comment = translate_comment($comment);
        my $trans = "$key = $value $comment\n";

        $by_pos->{$p} = $trans;

        $count1 += 1;
    }

    print "$count1 constants found\n";
}

sub process_functions {
    my $code = shift;
    my $by_pos = shift;

    # First use a simple regex, to be sure of counting all examples
    my $count1 = 0;
    # "OVR_PUBLIC_FUNCTION(ovrResult) ovr_Initialize(const ovrInitParams* params);"
    while ($code =~ m/\n[^\/\#]*OVR_PUBLIC_FUNCTION\(/g) {
        $count1 += 1;
    }

    my $count2 = 0;
    # "OVR_PUBLIC_FUNCTION(ovrResult) ovr_Initialize(const ovrInitParams* params);"
    while ($code =~ m/
            ((?:$comment_line_rx)*) # Previous block of comment lines
            (?<=\n)
            [^\/\#]* # beginning of line with no comments
            OVR_PUBLIC_FUNCTION
            \(
            ($type_rx) # return type
            \)\s*
            ($ident_rx) # function name
            \(
            ([^\)]*) # argument list
            \)
            ;\n
            /gx) 
    {
        my $comment = $1;
        my $return_type = $2;
        my $fn_name = $3;
        my $argument_list = $4;
        my $p = pos($code) - length($&);

        $return_type = translate_type($return_type);
        my $py_fn_name = translate_function_name($fn_name);

        # Return type for ctypes function
        my $trans = "libovr.$fn_name.restype = $return_type\n";
        my @arg_names = ();
        my @arg_types = ();
        my %types_by_arg = ();
        my %byref_args = ();

        # Argument types for ctypes function
        if (defined($argument_list) and $argument_list =~ m/\S/) {
            $trans .= "libovr.$fn_name.argtypes = [";
            my @args = split '\s*,\s*', $argument_list;
            foreach my $arg (@args) {
                die $arg unless $arg =~ m/^
                        ($type_rx)\s+
                        ($ident_rx)
                        (\[\d*\])?$/x;
                my $type = $1;
                my $ident = $2;
                my $decoration = $3;

                $type = translate_type($type);
                # Fixed-size array return value
                if (! defined $decoration) {}
                elsif ($decoration =~ m/^\[(\d+)\]$/) {
                    $type = "$type * $1";
                }
                # Unspecified array type return value
                elsif ($decoration =~ m/^\[\]$/) {
                    $type = "POINTER($type)";
                }

                if ($type =~ /^POINTER\(/) {
                    $byref_args{$ident} = 1;
                }

                # Avoid warning for use of "format" as an identifier per jherico
                $ident =~ s/^format$/format_/;

                push @arg_names, $ident;
                push @arg_types, $type;
                $types_by_arg{$ident} = $type;
            }
            $trans .= join ", ", @arg_types;
            $trans .= "]\n";
        }

        # Maybe create local variable for out parameters
        my @out_args = ();
        my %out_args_set = ();
        if (defined $comment) {
            # Search function docstring for output parameters
            while ($comment =~ m/\\param\[out\]\s*(\S+)/g) {
                my $arg_name = $1;
                # All output arguments of non-array type get special treatment
                if (! exists $types_by_arg{$arg_name}) {
                    # print "Argument not found! $fn_name : $arg_name \n";
                    # Hard code luid => pLuid
                    $arg_name = "p".ucfirst($arg_name);
                }
                if ($types_by_arg{$arg_name} !~ m/ \* /) {
                    push @out_args, $arg_name;
                    $out_args_set{$arg_name} = 1;
                    $byref_args{$arg_name} = 1;
                }
            }
        }
        my @input_args = ();
        foreach my $arg (@arg_names) {
            if (! exists $out_args_set{$arg}) {
                push @input_args, $arg;
            }
        }

        # Python wrapper for function
        $trans .= "def $py_fn_name(";
        $trans .= join ", ", @input_args;
        $trans .= "):\n";
        # Docstring
        $trans .= translate_docstring_comment($comment);

        # Special case for submitFrame method
        foreach my $arg (@arg_names) {
            # Only non-output POINTER(POINTER(...)) arguments.
            # i.e. Only submitFrame(layerPtrList) argument.
            next unless exists $byref_args{$arg};
            next if exists $out_args_set{$arg};
            next unless $types_by_arg{$arg} =~ m/^POINTER\((POINTER\(\S*\s*\))\s*\)/;
            # print $types_by_arg{$arg}, "\n";
            # print $arg, "\n";
            my $pointee_type = $1;
            # print $pointee_type, "\n";
            $trans .= "    $arg = ($pointee_type * len($arg))(*[ctypes.pointer(i) for i in $arg])\n";
        }        

        # Declare local variables for output arguments
        foreach my $arg (@out_args) {
            my $type = $types_by_arg{$arg};
            $type =~ s/^POINTER\((.*)\)$/$1/;
            $trans .= "    $arg = $type()\n";
        }

        # Wrap output args with "byref"
        my @call_args = ();
        foreach my $arg (@arg_names) {
            if (exists $byref_args{$arg}) {
                $arg = "byref($arg)";
            }
            # Wrap Bool args with "toOvrBool()"
            my $type = $types_by_arg{$arg};
            if (defined($type) and $type =~ m/^Bool$/) {
                $arg = "toOvrBool($arg)";
            }
            push @call_args, $arg;
        }

        # Delegated function call
        $trans .= "    result = "; # indent function call
        $trans .= "libovr.$fn_name(";
        $trans .= join ", ", @call_args;
        $trans .= ")\n";

        # Handle OVR specific return codes
        if ($return_type =~ m/^Result$/) {
            # TODO: 
            $trans .= <<EOF;
    if FAILURE(result):
        raise Exception(\"Call to function $py_fn_name failed\")    
EOF
        }
        my @return_items = ();
        # Limit return values to important ones
        if ($#out_args >= 0) {
            if ($return_type =~ m/^None$/) {}
            elsif ($return_type =~ m/^Result$/) {}
            else {
                push @return_items, "result";
            }
            push @return_items, @out_args;
        }
        else {
            # Might as well return result var, if it's the only output
            push @return_items, "result";
        }
        if ($#return_items >= 0) {
            my $returns = join ", ", @return_items;
            $trans .= "    return $returns\n";
        }

        $by_pos->{$p} = $trans;

        $count2 += 1;
    }

    # print "$count1 ($count2) functions found\n";
    die unless $count1 == $count2;
};

sub process_structs {
    my $code = shift;
    my $by_pos = shift;

    # First use a simple regex, to be sure of counting all examples
    my $count1 = 0;
    # skip structs without bodies
    # skip the word "struct" within a comment
    while ($code =~ m/\n[^\/]*\b(struct|union)\b[^;]*\{/g) 
    {
        $count1 += 1;
    }

    my $count2 = 0;
    while ($code =~ m/
        ((?:$comment_line_rx)*) # Previous block of comment lines
        (?<=\n)
        \btypedef\b
        \s+
        \b(struct|union)\b
        (?:\s+OVR_ALIGNAS\(([^)]+)\))? # optional memory alignment
        \s+
        \S+ # structed class name
        \s*
        \{
        ([^\}]*)
        \}
        \s*
        (\S+) # primary class name
        \s*
        ;
        /gx) 
    {
        my $comment = $1;
        my $struct_or_union = $2;
        my $alignment = $3;
        my $body = $4;
        my $class_name = $5;
        my $p = pos($code) - length($&);

        $class_name = translate_type($class_name);

        my $trans = "";
        $trans .= "class $class_name(";
        if ($struct_or_union =~ m/^struct$/) {
            $trans .= "Structure";
        }
        else {
            $trans .= "Union";            
        }
        $trans .= "):\n";

        if (defined($comment)) {
            # Use comment as docstring
            $comment =~ s/^\s+|\s+$//g; # trim terminal whitespace
            $comment =~ s!^([^/]*)/+\*? ?(.*)$!$1$2!mg; # remove comment characters
            if ($comment =~ /\n/) {
                # Multiline comment
                $trans .= "    \"\"\"\n";
                foreach my $line (split "\n", $comment) {
                    # $line =~ s/^\s*//;
                    $trans .= "    $line\n";
                }
                $trans .= "    \"\"\"\n";
            }
            else {
                $trans .= "    \"$comment\"\n";
            }
        }

        if (defined($alignment)) {
            $trans .= "    _pack_ = $alignment\n";
        }

        $trans .= "    _fields_ = [\n";

        my @fields = ();

        foreach my $line (split "\n", $body) {
            # "int w, h;"
            next if $line =~ m/^\s*$/; # skip blank lines
            if ($line =~ m/
                ^
                \s*
                ($type_rx)
                \s+
                ((?:$ident_rx,?\s*)*)
                (?:\[([^\]]+)\]\s*)? # first array dimension
                (?:\[([^\]]+)\]\s*)? # second array dimension "M[4][4]"
                ;
                (.*) # rest of line (comment?)
                $
                /x) 
            {
                my $type = $1;
                my $identifiers = $2;
                my $count = $3;
                my $count2 = $4;
                my $rest = $5;

                $rest = translate_comment($rest);
                $type = translate_type($type);
                if (defined $count) {
                    $count = translate_type($count);
                    $type = "$type * $count";
                }
                if (defined $count2) {
                    $count2 = translate_type($count2);
                    $type = "($type) * $count2";
                }
                foreach my $ident (split ",", $identifiers) {
                    $ident =~ s/^\s+|\s+$//g; # trim white space
                    $ident = translate_ident($ident);
                    $trans .= "        (\"$ident\", $type), $rest\n";
                    my @p = ($ident, $type);
                    push @fields, \@p;
                }
            }
            elsif ($line =~ m/^
                \s*
                OVR_UNUSED_STRUCT_PAD\(
                (\S+)
                ,\s*
                (\S+)
                \)
                (.*)
                $/x) 
            {
                my $id = $1;
                my $pad = $2;
                my $rest = $3;

                $rest = translate_comment($rest);

                $trans .= "        (\"$id\", c_char * $pad), $rest\n";
            }
            elsif ($line =~ m/^
                \s*
                OVR_ON64\(
                OVR_UNUSED_STRUCT_PAD\(
                (\S+)
                ,\s*
                (\S+)
                \)
                (.*)
                /x) 
            {
                my $id = $1;
                my $pad = $2;
                my $rest = $3;

                $rest = translate_comment($rest);
                # TODO: eventually handle 64-bit padding correctly
                $trans .= "        # skipping 64-bit only padding... # (\"$id\", c_char * $pad), $rest\n";
            }
            else {
                $line = translate_comment($line);
                $line  =~ s/^\s+|\s+$//g; # trim white space
                $trans .= "        $line\n";
            }
        }
        $trans .= "    ]\n"; # end fields

        # String representation
        $trans .= "\n    def __repr__(self):\n        return \"ovr.$class_name(";
        my $s = $#fields + 1;
        $trans .= join ", ", ("%s") x $s;
        $trans .= ")\" % (";
        my @args = ();
        foreach my $f (@fields) { # arguments
            my $field = $f->[0];
            push @args, "self.$field";
        }
        $trans .= join ", ", @args;
        $trans .= ")\n";

        # Custom methods
        if (exists $custom_methods{$class_name}) {
            foreach my $method (@{$custom_methods{$class_name}}) {
                $trans .= $method;
            }
        }

        $by_pos->{$p} = $trans;

        $count2 += 1;
    }

    # print "$count1 ($count2) structs found\n";
    die unless $count1 == $count2;
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
        my $p = pos($code) - length($&);

        # Remove OVR_ prefix
        $fn_name =~ s/\bOVR_//g;
        $fn_body =~ s/\bOVR_//g;

        # Translate not
        $fn_body =~ s/!/not /g;

        my $trans = "def $fn_name($args):\n    return $fn_body\n";

        $by_pos->{$p} = $trans;
        $count1 += 1;
    }

    # print $count1, " macros found\n";

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
        my $p = pos($code) - length($&);

        my $trans = "";

        $comment = translate_comment($comment);
        if (defined $comment) {
            $trans .= "$comment";
        }

        # 1) Declare type alias for enum
        $enum_name = translate_type($enum_name);
        $trans .= "$enum_name = ENUM_TYPE\n";
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

                # Skip "foo_EnumSize" entries
                next if $id =~ m/_EnumSize/;

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
        my $p = pos($code) - length($&);

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
    # C strings
    if ($type =~ m/^\s*(?:const\s+)?char\s*\*\s*$/) {
        $type = "c_char_p"; # strings
    }
    $type =~ s/\blong\s+long\b/longlong/;
    if ($type =~ m/^(float|u?int|double|u?char|u?short|u?long)/) {
        $type = "c_$type";
    }
    # remove leading "ovr" or "ovr_"
    if ($type =~ m/^ovr_?(.*)$/) {
        $type = ucfirst($1); # capitalize first letter of types
    }
    # translate pointer type "*"
    while ($type =~ m/^([^\*]+\S)\s*\*(.*)$/) { # HmdStruct* -> POINTER(HmdStruct)
       $type = "POINTER($1)$2";
    }
    # translate pointer type "ptr"
    while ($type =~ m/^([^\*]+)ptr(.*)$/) { # uintptr_t -> POINTER(c_uint)
       $type = "POINTER($1)$2";
    }

    if ($type =~ /^void$/) {
        $type = "None";
    }

    return $type;
}

sub translate_docstring_comment {
    my $comment = shift;
    my $trans = "";

    if (defined($comment)) {
        # Use comment as docstring
        $comment =~ s/^\s+|\s+$//g; # trim terminal whitespace
        $comment =~ s!^([^/]*)/+\*? ?(.*)$!$1$2!mg; # remove comment characters
        if ($comment =~ m/^\s*$/) {} # no content
        elsif ($comment =~ /\n/) {
            # Multiline comment
            $trans .= "    \"\"\"\n";
            foreach my $line (split "\n", $comment) {
                # $line =~ s/^\s*//;
                $trans .= "    $line\n";
            }
            $trans .= "    \"\"\"\n";
        }
        else {
            $trans .= "    \"$comment\"\n";
        }
    }
}

sub translate_function_name {
    my $fn_name = shift;
    $fn_name =~ s/^ovr_?//;
    return lcfirst($fn_name);
}
