#!/usr/bin/perl -w
#
# ca-getmod_srf.pl
#
# Created by MDWilliams, INTERA 11-14-2018
#      This program reads the surface fluxes from a vadose zone run
#      and creates a file for plotting of a specified solute
#      
#
#  Arguments:
#  	STOMP input file name
#  	Keyword in surface flux cards (solute)
#	Units
#	Top or Bot
#  	Output file prefix (model-name)
#
#  Version Log:
#  1.3 = original version 11-20-2018
#
#  1.4 = creating a second file for modflow input - yearly and units of pCi and ug.
#
#  1.5 = Added plot with modflow grid blocks, total rads, wastesites
#  
#  1.6 - Bug fix on modflow file.  One year off on interpolated instantaneous rate.
#
#  1.7 - Added plot with waste sites and modflow grid - using gnuplot files instead 
#        of csv files.  The only difference is a blank line between polygons
#  
#  1.8 - Bugs fixes - zeros in yearly interpolation, checking instanteous max instead of
#        cummulative for whether to generate btcs gnuplots
#
#  1.9 - Made thresholds for P2R grid plot and BTC's the same 1 nanocurie.
#
#  2.0 - Removed annual file generation (now done outside facet)
#
#  3.0 - Added Top and Bot parameters - Dennis now creates Modflow Surfaces at the top of the
#        Domain to see what came into the domain.
#
#  4.0 - Bug fixes, Top was flaky, some scales get hosed
#
#  5.0 - Added plots for total bottom flux
# 
#  5.2 - bug fix - some multplots are screwed up
#
#  6.1 - New domain file changes (all in one csv file), new format of modeflow.gnu file
#
#  6.2 = Fixing plots, additing source cummulatives
#
#  7.1 = removed plotting (now part of ca-plotmodsurfs)
#
#  7.2 fixed a bug reported by dennis - 
# 	FROM if ($sfcol[$s] != $sfcol[$s]) TO if ($sfcol[0] != $sfcol[$s])

use Scalar::Util qw(looks_like_number);
$dtstamp = localtime();

$vers = "ca-getmod_srf.pl, Intera Inc, generated on $dtstamp";

$ifile = shift @ARGV;
$kw = shift @ARGV;
$keyword=lc($kw);
$conc = shift @ARGV;
$torb = shift @ARGV;
$prefix = shift @ARGV;

$torb=lc($torb);
if (($torb ne "top") && ($torb ne "bot")) {
	printf("Error - invalid TOP or BOT argument = $torb\n");
	exit(0);
}

$dfile = $prefix."-$keyword-$torb.csv";
$cfile = $prefix."-$keyword-cumulative-$torb.csv";

open(FI,"<$ifile") ||  die "Can't open $ifile file $!\n";
open(FD,">$dfile") ||  die "Can't open $dfile file $!\n";
#open(FM,">$mfile") ||  die "Can't open $mfile file $!\n";
open(FC,">$cfile") ||  die "Can't open $cfile file $!\n";

# Skip to surface flux cards
$flag = 0;
$line="";
while (($flag == 0) && ($line = <FI>)) {
	chomp($line);
	if (lc($line) =~ m/\~surface flux/i) {
		$flag = 1;
		printf("Got a surface flux card match\n");
	}
}
if ($flag == 0) {
	printf("Error - no surface flux card found\n");
	exit(0);
} 

# loop for number of cards looking for grid groups and keyword
# Get # of Cards
$nfc=-1;
$cfc=0;
$nsrc=0;
@sfname = [];
@sfpname = [];
@sfcol = [];
@sfcomment = [];
@sfline = [];
$gflag = 0;
$sflag = 0;
while (($cfc != $nfc) && ($line = <FI>)) {
   chomp($line);
   @a = split(",",$line);
   if ($gflag == 0) {
	# not in a group, skip comments
	if (substr($line,0,1) ne "#") {
	    if ($nfc != -1) {
	    	# gotta group
	    	$ng = $a[0];
		$cg = 0;
	    	$gflag = 1;
	    	$gfname = $a[1];
#		printf("Got a Group $ng, $gfname\n");
	    } else {
	    	# number of surface flux cards / groups
	    	$nfc=$a[0];
#		printf("NFC = $nfc\n");
	    }
	}
    } else {
	# within a group - see if this is one we care about
	if (substr($line,0,1) eq "#") {
	   # check comments for special line identifying 100 m grid block
	   if (((lc($torb) eq "bot") && ($line =~ m/Bottom Flux for P2R/i)) || 
		((lc($torb) eq "top") && ($line =~ m/Top Flux for P2R/i))) {
		   # we want this ...
#			printf("We Got one: $line\n");
			$sfname[$nsrc]=$gfname;
			@a=split("/",$gfname);
			if (scalar(@a) > 1) {
				$sfpname[$nsrc]=$a[1]; 
			} else {
				$sfpname[$nsrc]=$gfname;
			}
			$sfpname[$nsrc] =~ s/\.srf//;
			$sfpname[$nsrc] =~ s/_top//;
			$sfcomment[$nsrc]=$line;
			$sflag = 1;
	   }
   	} else {
	   # got a real surface flux line
	   $cfc++;	   
	   $cg++;
	   $chkkey = $a[1];
	   $chkkey  =~ s/^\s+|\s+$//g;
	   $chkkey = lc($chkkey);
#printf("chkkey = \#$chkkey\# Keyword = \#$keyword\#\n");
	   if (($sflag ==1) && ($chkkey eq $keyword)) {
		$sfcol[$nsrc]=$cg;
		$sfline[$nsrc]=$line;
#		printf("nsrc=$nsrc, sfcol=$sfcol[$nsrc] sfname=$sfname[$nsrc]\n");
		$nsrc++;
	   }
	   if ($cg == $ng) {
		# end of a group
		$gflag = 0;
		$sflag = 0;
#		printf("cfc, nfc = $cfc,$nfc\n");
	   }

   	}
    }
}
close(FI);

# Read Surface Flux Files, Calulate and Write Sources
if ((lc($conc) eq "ci") || (lc($conc) eq "kg") || (lc($conc) eq "g")) {
} else {
	printf("Error - unrecognized Units on command line = ($conc)\n");
	exit(1);
}
printf(FD "#### \n# Created by ca-getmod_srf.pl\n");
printf(FD "# $vers \n####\n");
printf(FD "# Keyword = $keyword\n# \n");
#printf(FM "#### \n# Created by ca-getmod_srf.pl\n");
#printf(FM "# $vers \n####\n");
#printf(FM "# Keyword = $keyword\n# \n");
printf(FC "#### \n# Created by ca-getmod_srf.pl\n");
printf(FC "# $vers \n####\n");
printf(FC "# Keyword = $keyword\n# Cumulative Summary\n");

for ($s=0;$s<$nsrc;$s++) {
	$fl[$s]=0;
	$uflag = 0;
	$fdimax[$s]=0.0;
	# open surface flux output file and load data
	print(" filename = $sfname[$s]\n");
	open(FS,"<$sfname[$s]") ||  die "Can't open $sfname[$s] file $!\n";
	while ($line = <FS>) {
	    chomp($line);
	    if (($line=~/    Time/) && ($uflag==0)) {
		# get next line for units
		$line = <FS>;
		chomp($line);
		@a = split("]",$line);
		for ($i=0;$i<scalar(@a);$i++) {
#			printf("$a[$i] ");
			$a[$i] =~ tr/[//d;
			$a[$i] =~ s/^\s+|\s+$//g;
			$a[$i] =~ s/sol/$conc/;
			$a[$i] =~ s/1\//$conc\//;
			$units[$i]=$a[$i];
#			printf("Units: $units[$i]\n");
		}
		$uflag=1;
	    } else {
		# remove leading and trailing whitespaces
		$line =~ s/^\s+|\s+$//g;
		@a=split(" ",$line);
		if (scalar(@a) > 0) {
		   if (looks_like_number($a[0])) {
			# not a header line
#print("$line\n");
#printf("$a[0],$sfcol[$s],$a[$sfcol[$s]*2]\n");
			$ft[$s][$fl[$s]]=$a[0];
			$col=(($sfcol[$s]-1)*2)+1;
			$fdi[$s][$fl[$s]]=$a[$col];
			if ($a[$col] > $fdimax[$s]) {
				$fdimax[$s]=$a[$col];
			}
			$fdc[$s][$fl[$s]]=$a[$col+1];
			$fl[$s]++;
		   }
		}
	    }
	}
	close(FS);
}
# check that all columns are the same in the surface file
for ($s=1;$s<$nsrc;$s++) {
	if ($sfcol[0] != $sfcol[$s]) {
		printf("Columns don't match in surf files: $s, $sfcol[0], $sfcol[$s], $sfname[$s]\n");
	}

	# check times in srf files - make sure all the same
	if ($fl[0] != $fl[$s]) {
		printf("Error - number of surf lines dont match: $s, $fl[0], $fl[$s], $sfname[$s]\n");
	}
	for ($i=0;$i<$fl[$s];$i++) {
		if ($ft[0][$i] != $ft[$s][$i]) {
		    printf("Error - Times don't match: $s, $ft[0][$i], $ft[$s][$i], $sfname[$s]\n");
		}
	}
}


# write flux file
printf(FD "# Solute = $keyword\n");
printf(FD "Time,");
for ($s=0;$s<$nsrc;$s++) {
	printf(FD "$sfpname[$s],,");
}
printf(FD "\n");
printf(FD ",");
for ($s=0;$s<$nsrc;$s++) {
        printf(FD "Instantaneous,Cumulative,");
}
printf(FD "\n");
printf(FD "$units[0],");
for ($s=0;$s<$nsrc;$s++) {
	$col = (($sfcol[$s]-1)*2)+1;
        printf(FD "$units[$col],$units[$col+1],");
}
printf(FD "\n");
for ($j=0;$j<$fl[0];$j++) {
    printf(FD "%.6e,",$ft[0][$j]);
    for ($s=0;$s<$nsrc;$s++) {
        printf(FD "%.6e,%.6e,",$fdi[$s][$j],$fdc[$s][$j]);
    }
    printf(FD "\n");
}
close(FD);

# Write out cummulative Table
#$syear=int($ft[0][0]);
$eyear=int($ft[0][$fl[0]-1]);

printf(FC "$torb,\n");
printf(FC "name,Total Cumulative,Total at $eyear,25%% Time, 50%% Time, 75%% Time, 99%% Time\n");
$col=(($sfcol[0]-1)*2)+1;
$max99time=0.0;
$maxnano=0.0;
printf(FC ",$units[$col+1],$units[$col+1],$units[0],$units[0],$units[0],$units[0]\n");
for ($s=0;$s<$nsrc;$s++) {
        $col=(($sfcol[$s]-1)*2)+1;
        $tot=$fdc[$s][$fl[$s]-1];
        $clast = 0.0;
        $t25=0.0;
        $c25=$tot*0.25;
        $t50=0.0;
        $c50=$tot*0.50;
        $t75=0.0;
        $c75=$tot*0.75;
        $t99=0.0;
        $c99=$tot*0.99;
        for ($j=0;$j<$fl[$s];$j++) {
                $c=$fdc[$s][$j];
                $t=$ft[$s][$j];
                if (($fdi[$s][$j] >= 1.0E-9) && ($t > $maxnano)) {
                        $maxnano=$t;
                }

                if (($clast == 0.0) && ($t>=$eyear)) {
                        $clast = $c;
                }
                if (($t25 == 0.0) && ($c>=$c25)) {
                        $t25=$t;
                }
                if (($t50 == 0.0) && ($c>=$c50)) {
                        $t50=$t;
                }
                if (($t75 == 0.0) && ($c>=$c75)) {
                        $t75=$t;
                }
                if (($t99 == 0.0) && ($c>=$c99)) {
                        $t99=$t;
                        if ($t > $max99time) {
                                $max99time=$t;
                        }
                }
        }
        printf(FC "$sfpname[$s],$tot,$clast,$t25,$t50,$t75,$t99\n");
}
close(FC);

