#!/usr/bsn/perl -w
# $RCSfile$ $Date$ $Author$ $Revision$
# ca-rtdic.pl (formerly part of ca-icdup.pl)
# Created by MDWilliams, 6-12-2019
#	Scans the input source card file and generates the following:
#	IC Cards for RTD restarts
#	Version 1.5 - variable header lines in RTD Site List
#
#       Version 2.1 - Now scanning cars for Ktop min and max to set the K's for ICs
#		      The Source cards use Ktop min, but the IC Cards need to use the
#		      Ktop max (in case any solute got up there).
#	version 2.3 - only the rtd portion (removed the dup check)
#
#       version 2.4 - removed extra spaces
#
#	version 2.5 - renamed from ca-rtd to ca-rtdic
#
#	version 2.8 - getting ktop min and max from .card file
#
#	version 3.1 - getting ktop max from grid file and ktopmin from .card file. note that is also makes sure
#		      the ktop min is consistent for each waste site (lowest ktopmin).

$dtstamp = localtime();

$vers="ca-rtdic 5/2/2020 Ver 3.1 by MDWilliams, Intera Inc";
# get and open source list file (created by ca-src2stomp.pl)
$sf = shift @ARGV;  # src card file
$icl = shift @ARGV; # RTD Site list: waste site name, excavation depth, number of nodes to clear below bottom.
$inpf = shift @ARGV; # stomp input file
$icf = shift @ARGV; # output IC file for RTD restarts

# get list of solutes from command line
$nsol = scalar(@ARGV);
printf("nsol=$nsol\n");
@sol=[];
for ($i=0;$i<$nsol;$i++) {
	$sol[$i]=shift @ARGV;
	printf("$sol[$i]\n");
}

open(SL,"<$sf") ||  die "Can't open $sf file $!\n";
open(IN,"<$inpf") ||  die "Can't open $inpf file $!\n";
open(IC,">$icf") ||  die "Can't open $icf file $!\n";

printf(IC "# $vers\n");
printf(IC "# Generated from $sf on $dtstamp\n");
printf(IC "#\n");

# get grid card from input file to for setting ztopmax (global)
$flag=0;
while ($line=<IN>) {
        chomp($line);
        if ($line =~ m/~grid/i) {
                $flag = 1;
                # skip two lines to get to nx,ny,nx
                $line=<IN>;
                $line=<IN>;
                $line=<IN>;
                chomp($line);
                @a=split(",", $line);
#               $nx=$a[0];
#               $ny=$a[1];
                $nz=$a[2];
                $globalktop = $nz;
                last;
        }
}
if ($flag == 0) {
        printf("Error - could not find grid card in $inpf\n");
        exit(0);
}
close(IN);


$nrtd=0;
@rtdname=[];
@rtdzdown=[];
open(IL,"<$icl") ||  die "Can't open $icl file $!\n";
# skip header
$line=<IL>;
chomp($line);
while (substr($line,0,1) eq "#") {
	$line=<IL>;
       	chomp($line);
}
$ilflag=0;
while ($ilflag == 0) {
	@a=split(",", $line);
	$rtdname[$nrtd]=$a[0];
	$rtdname[$nrtd]=~s/^\s+|\s+$//g;
#	printf("RTD Name = $rtdname[$nrtd]\n");
	# skip depth = only for comment
	$rtdzdown[$nrtd]=$a[2];
	$nrtd++;
	if (eof(IL)) {
               $ilflag=1;
        } else {
		$line=<IL>;
		chomp($line);
	}
}
close(IL);

# scan source code file
# find first non-comment and skip Source Card Header
$line="";
while ($line = <SL>) {
	chomp($line);
	$c=substr($line,0,1);
	if (($c ne "#") && ($line !~ m/~Source Card/i)) {
		last;
	}
		
}
# skip number of sources
$line = <SL>;


$flag = 0;
$nlines=0;
$ns=0;
@snames = [];
@ijlist = [];
@nij = [];
@ktopmax = [];
@ktopmin = [];
$nhash = {};
while ($flag == 0) {
	# find site name
	$sn = "";
	while ($line = <SL>) {
		chomp($line);
		if ($line =~ m/# Site = /i) {
			@a=split("# Site = ",$line);
			$sn=$a[1];
			$sn=~s/^\s+|\s+$//g;
			if (exists ($nhash{$sn})) {
				$s=$nhash{$sn};
			} else {
				$nhash{$sn} = $ns;
				$snames[$ns]=$sn;
				$s=$ns;
				$nij[$s]=0;
				$ktopmax[$s]=0;
				$ktopmin[$s]=9999999;
				$ns++;
			}
			last;
		}
	}
	if (eof(SL)) {
		$flag=1;
		last;
	}
	if ($sn eq "") {
		$flag = 1;
		last;
	}
	$c="";
	# skip to cards
	while ($line = <SL>) {
                chomp($line);
		$c=substr($line,0,1);
        	if ($c ne "#") {
                	last;
		} 
        }
	if (eof(SL)) {
		$c="#";
		$flag=1;
		last;
	}
	while ($c ne "#") {
		@a=split(",",$line);		
		# remove leading and trailng white spaces
	    	for ($i=0;$i<scalar(@a);$i++) {
			$a[$i] =~ s/^\s+|\s+$//g;
		}
		if ($a[0] =~ m/solute/i) {
			$ind=$a[2].",".$a[3].",".$a[4].",".$a[5];
			$kmin=$a[6];
			$kmax=$a[7];
			$nlines=$a[8];
		} else {
			$ind=$a[1].",".$a[2].",".$a[3].",".$a[4];
			$kmin=$a[5];
			$kmax=$a[6];
			$nlines=$a[7];
		}
		$hit=0;
		printf("$nij[$s]\n");
		for ($i=0;$i<$nij[$s];$i++) {
			if (!defined($ind)) {
				printf("Error - ind not defined");
				exit(0);
			}
			if (!defined($ijlist[$s][$i])) {
				printf("Error - ijlist[s] not defined");
				exit(0);
			}
			printf("$ind $ijlist[$s][$i]\n");
			if ($ind eq $ijlist[$s][$i]) {
				printf("matched $ind\n");
				$hit=1;
				if ($kmax > $ktopmax[$s]) {
					$ktopmax[$s]=$kmax;
				}
				if ($kmin < $ktopmin[$s]) {
					$ktopmin[$s]=$kmin;
				}
			}
		}
		if ($hit == 0) {
			$ijlist[$s][$nij[$s]]=$ind;
			$ktopmin[$s]=$kmin;
			$ktopmax[$s]=$kmax;
			$nij[$s]++;
			printf("adding $ind\n");
		}

                # get year lines
                for ($i=0;$i<$nlines;$i++) {
                        $line=<SL>;
                }
                if (eof(SL)) {
                        $flag=1;
                        last;
                }
                $line = <SL>;
                chomp($line);
                $c=substr($line,0,1);
        }
}
		
for ($s=0;$s<$ns;$s++) {
	# see if it matches RTD sites
	for ($r=0;$r<$nrtd;$r++) {
		if ($snames[$s] eq $rtdname[$r]) {
                        printf(IC "# Site = $snames[$s]\n");
			printf("Matched IC Site = $snames[$s]\n");
		    	for ($i=0;$i<$nsol;$i++) {
			    for ($l=0;$l<$nij[$s];$l++) {
                       		printf(IC "Overwrite Solute Volumetric Concentration,");
                       		printf(IC "$sol[$i], 0.0, 1/L, , , , , , ,");
                       		$bot = $ktopmin[$s]-$rtdzdown[$r];
                       		printf(IC "$ijlist[$s][$l],$bot,$globalktop,\n");
			    }
		    	}
		}
	}
}

close(SL);
close(IC);

