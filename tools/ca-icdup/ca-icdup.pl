#!/usr/bsn/perl -w
# $RCSfile$ $Date$ $Author$ $Revision$
# ca-icdup.pl
# Created by MDWilliams, 6-12-2019
#	Scans the input source card file and generates the following:
#	IC Cards for RTD restarts
#	Reports duplicate sources to the same node
#	Version 1.5 - variable header lines in RTD Site List
#
$dtstamp = localtime();

$vers="ca-icdup 7/22/2019 Ver 1.5 by MDWilliams, Intera Inc";
$dtstamp = localtime();
# get and open source list file (created by ca-src2stomp.pl)
$sf = shift @ARGV;  # src card file
$icl = shift @ARGV; # RTD Site list: waste site name, excavation depth, number of nodes to clear below bottom.
$icf = shift @ARGV; # output IC file for RTD restarts
$rf = shift @ARGV;  # output report file

# get list of solutes from command line
$nsol = scalar(@ARGV);
printf("nsol=$nsol\n");
@sol=[];
for ($i=0;$i<$nsol;$i++) {
	$sol[$i]=shift @ARGV;
	printf("$sol[$i]\n");
}

open(SL,"<$sf") ||  die "Can't open $sf file $!\n";
open(IC,">$icf") ||  die "Can't open $icf file $!\n";
open(SR,">$rf") ||  die "Can't open $rf file $!\n";

printf(SR "# $vers\n");
printf(IC "# $vers\n");
printf(IC "# Generated from $sf on $dtstamp\n");
printf(IC "#\n");

$nrtd=0;
@rtdname=[];
@rtdzdown=[];
if (lc($icl) ne "all") {
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
		printf("RTD Name = $rtdname[$nrtd]\n");
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


# scan source code file
# find first non-comment and skip Source Card Header
$line="";
while ($line = <SL>) {
	chomp($line);
	$c=substr($line,0,1);
	if (($c ne "#") && ($c ne "~")) {
		@a=split(",",$line);
		$nc = $a[0];
		last;
	}
		
}

printf("nc = $nc\n");

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
		chomp($line);
		if ($line =~ m/# Site = /i) {
			@a=split("# Site = ",$line);
			$sname=$a[1];
			$sname=~s/^\s+|\s+$//g;
			printf("sname=$sname\n");
			last;
		}
	}

	# skip to source data for this site
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
                        }
			@b=split(",",$ind);
			for ($i=0;$i<$nsol;$i++) {
                        	printf(IC "Overwrite Solute Volumetric Concentration,");
                        	printf(IC "$sol[$i], 0.0, 1/L, , , , , , ,");
                        	$bot = $b[4]-$zrbot;
                        	printf(IC "$b[0],$b[1],$b[2],$b[3], $bot, TOP,\n");
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

# check for dups
$sep="------------------------";
$nhash = {};
printf(SR "Number of sources = $nsrc\n");
printf(SR "Number of source nodes = $nn\n");
for ($n=0;$n<$nn;$n++) {
#	print("nkey=$nkey[$n]\n");
	if (exists $nhash{$nkey[$n]}) {
		# possible dup - check years
		$dn=$nhash{$nkey[$n]};
		$ndy=0;
		@dy=[];
		printf(SR "$sep\n");
		printf(SR "Possible dup: $nkey[$n]\n");
		printf(SR "    $nname[$n]\n");
		for ($i=0;$i<$nyears[$n];$i++) {
			printf(SR "$ny[$n][$i], ");
		}
		printf(SR "\n");
		printf(SR "    $nname[$dn]\n");
		for ($i=0;$i<$nyears[$dn];$i++) {
			printf(SR "$ny[$dn][$i], ");
			for ($j=0;$j<$nyears[$n];$j++) {
				if ($ny[$dn][$i] == $ny[$n][$j]) {
					$dy[$ndy]=$ny[$n][$j];
					$ndy++;
				}
			}
		}
		printf(SR "\n");
		if ($ndy != 0) {
			printf(SR "Dups on years also!\n");
			for ($i=0;$i<$ndy;$i++) {
				printf(SR "$dy[$i],");
			}
			printf(SR "\n");
		}

		printf(SR "$sep\n\n");

	} else {
		$nhash{$nkey[$n]}=$n;
	}
}

close(SL);
close(SR);
close(IC);

