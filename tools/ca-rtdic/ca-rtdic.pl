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
#	version 2.6 - getting ztopmax from input file grid card

$dtstamp = localtime();

$vers="ca-rtdic 4/29/2020 Ver 2.6 by MDWilliams, Intera Inc";
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
#		$nx=$a[0];
#		$ny=$a[1];
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
if (lc($icl) ne "all") {
   if (lc($icl) ne "none") {
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
#		printf("RTD Name = $rtdname[$nrtd]\n");
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
    }
}


# scan source code file
# find first non-comment and skip Source Card Header
$line="";
while ($line = <SL>) {
	chomp($line);
	$c=substr($line,0,1);
	if (($c ne "#") && ($c ne "~")) {
#		@a=split(",",$line);
#		$nc = $a[0];
		last;
	}
		
}


$flag = 0;
$nsrc=0;
$nlines=0;
$lsite="";
$ind_hash = {};
$nn=0;
@nname=[];
@nkey=[];
@nyears=[];
@ny=[];
while ($flag == 0) {
	# find site name
	while ($line = <SL>) {
		$sname = "";
		chomp($line);
		if ($line =~ m/# Site = /i) {
			@a=split("# Site = ",$line);
			$sname=$a[1];
			$sname=~s/^\s+|\s+$//g;
#			printf("sname=$sname\n");
			last;
		}
	}

	# skip to source data for this site
	if ($sname eq "") {
		$flag = 1;
		last;
	}
	$c="";
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
	}
	while ($c ne "#") {
		@a=split(",",$line);		
		# remove leading and trailng white spaces
	    	for ($i=0;$i<scalar(@a);$i++) {
			$a[$i] =~ s/^\s+|\s+$//g;
		}
		$nlines=$a[8];
		$ind="";
		if ($a[0] =~ m/solute/i) {
			$ind=$a[2].",".$a[3].",".$a[4].",".$a[5].",".$a[6].",".$a[7];
			$nkh=$a[0].",".$a[1];
			$nlines=$a[8];
		} else {
			$ind=$a[1].",".$a[2].",".$a[3].",".$a[4].",".$a[5].",".$a[6];
			$nkh=$a[0];
			$nlines=$a[7];
		}
		if (!(exists $ind_hash{$ind})) {
		    $ind_hash{$ind}=$ind;
		    $tflag = 0;
		    $zrbot = 8;
		    if (lc($icl) eq "all") {
			$tflag = 1;
		    } else {
			for ($i=0;$i<$nrtd;$i++) {
				if (lc($sname) eq lc($rtdname[$i])) {
					$tflag = 1;
					$zrbot = $rtdzdown[$i];
				}
			}
		    }
		    if ($tflag == 1) {
		 	if ($sname ne $lsite) {
                                printf(IC "# Site = $sname\n");
				printf("Matched IC Site = $sname\n");
                        }
			@b=split(",",$ind);
			for ($i=0;$i<$nsol;$i++) {
                        	printf(IC "Overwrite Solute Volumetric Concentration,");
                        	printf(IC "$sol[$i], 0.0, 1/L, , , , , , ,");
                        	$bot = $b[4]-$zrbot;
                        	printf(IC "$b[0],$b[1],$b[2],$b[3],$bot,$globalktop,\n");
                        	$lsite=$sname;
			}
		    }
		} 


		# get year lines
#		printf("nlines=$nlines\n");
		@y=[];
		for ($i=0;$i<$nlines;$i++) {
			$line=<SL>;
			chomp($line);
			@ys=split(",",$line);
			$y[$i]=$ys[0];
		}

		$nsrc++;
                # make list for dup check
                @b=split(",",$ind);
#		printf("nn=$nn $b[0],$b[1],$b[2],$b[3]");
                for ($i=$b[0];$i<=$b[1];$i++) {
                        for ($j=$b[2];$j<=$b[3];$j++) {
                        	$dkey=$nkh.",".$i.",".$j.",".$b[4];
				$nname[$nn]=$sname;
				$nkey[$nn]=$dkey;
				$nyears[$nn]=$nlines;
				for ($k=0;$k<$nlines;$k++) {
					$ny[$nn][$k]=$y[$k];
				}
				$nn++;
			}
		}
#		printf(" New nn=$nn\n");
		

		if (eof(SL)) {
			$flag=1;
			last;
		} 
		$line = <SL>;
#		printf("$line\n");
                chomp($line);
		$c=substr($line,0,1);
	}

}

close(SL);
close(IC);

