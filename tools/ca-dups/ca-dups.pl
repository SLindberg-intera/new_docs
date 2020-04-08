#!/usr/bsn/perl -w
# $RCSfile$ $Date$ $Author$ $Revision$
# ca-dups.pl (formerly part of ca-icdups).
# Created by MDWilliams, 6-12-2019
#	Scans the input source card file and generates the following:
#	IC Cards for RTD restarts
#	Reports duplicate sources to the same node
#	Version 1.5 - variable header lines in RTD Site List
#
#	version 2.3 - dups check only nodes, not time.
#
#	VERSION 2.4 FIXED VERSION DATE
#
#	version 2.5 - added a line "some" for sites that have dups.
#	
#	version 2.6 - removed unused variables

$vers="ca-dups 4/6/2020 Ver 2.6 by MDWilliams, Intera Inc";
$dtstamp = localtime();
# get and open source list file (created by ca-src2stomp.pl)
$sf = shift @ARGV;  # src card file
$rf = shift @ARGV;  # output report file

# get list of solutes from command line
$nsol = scalar(@ARGV);
#printf("nsol=$nsol\n");
@sol=[];
for ($i=0;$i<$nsol;$i++) {
	$sol[$i]=shift @ARGV;
#	printf("$sol[$i]\n");
}

open(SL,"<$sf") ||  die "Can't open $sf file $!\n";
open(SR,">$rf") ||  die "Can't open $rf file $!\n";

printf(SR "# $vers\n");
printf(SR "# run on $dtstamp\n");

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

#printf("number of sources = $nc\n");

$flag = 0;
$nsrc=0;
$nlines=0;
$nn=0;
@nname=[];
@nkey=[];
@srcnames=[];
$nsn=0;
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
	$srcnames[$nsn]=$sname;
	$nsn++;
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


		# get year lines
#		printf("nlines=$nlines\n");
#		@y=[];
		$line="";
		for ($i=0;$i<$nlines;$i++) {
			$line=<SL>;
#			chomp($line);
#			@ys=split(",",$line);
#			$y[$i]=$ys[0];
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
#				$nyears[$nn]=$nlines;
#				for ($k=0;$k<$nlines;$k++) {
#					$ny[$nn][$k]=$y[$k];
#				}
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
printf(SR "Number of sources = $nsrc\n");
printf(SR "Number of source nodes = $nn\n\n");
for ($s=0;$s<$nsn;$s++) {
    printf(SR "$sep\n");
    printf(SR "Source Name = $srcnames[$s]\n");
    printf(SR "Other Sources with x,y,z overlap:\n");
    $nmatch=0;
    for ($sn=0;$sn<$nn;$sn++) {
	if ($nname[$sn] eq $srcnames[$s]) {
		for ($n=0;$n<$nn;$n++) {
			if ($nname[$n] ne $srcnames[$s]) {
				if ($nkey[$n] eq $nkey[$sn]) {
				   	if ($nmatch == 0) {
						printf(SR "    some\n");
					}
                			$nmatch++;
                			printf(SR "    $nname[$n]\n");
                			printf(SR "        $nkey[$n]\n");
				}
			}
		}
 	  }
     }
     if ($nmatch == 0) {
         printf(SR "    none\n");
     }
     printf(SR "$sep\n\n");
}

close(SL);
close(SR);

