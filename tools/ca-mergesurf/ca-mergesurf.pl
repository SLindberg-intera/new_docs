#!/usr/bsn/perl -w
# $RCSfile$ $Date$ $Author$ $Revision$
# ca-mergesurf.pl
# Created by MDWilliams, 6-19-2019
#	Merges two stomp surface files.  Carries over
#	cumulative from end of first file to add to 
#	cumulatives in the second file
#	
#	
#

use Scalar::Util qw(looks_like_number);

$dtstamp = localtime();

$vers="ca-mergesurf 6/24/2019 Ver 1.3 by MDWilliams, Intera Inc";
# get and open source list file (created by ca-src2stomp.pl)
$slf = shift @ARGV; # get list of surface files
$fsd = shift @ARGV; # First surface file directory
$ssd = shift @ARGV; # Second surface file directory
$osd = shift @ARGV; # output combined surface file directory

open(SL,"<$slf") ||  die "Can't open $slf file $!\n";

# load file names
$nf=0;
@fn=[];
while ($line = <SL>) {
	chomp($line);
	# strip out first directory name
	$line =~ s/$fsd\///g;
#	printf("$line\n");
	$fn[$nf]=$line;
	$nf++;
}
close(SL);
#exit(0);
@a=[];
@b=[];
for ($f=0;$f<$nf;$f++) {
	$fsf=$fsd."\/".$fn[$f];
	$ssf=$ssd."\/".$fn[$f];
	$osf=$osd."\/".$fn[$f];
	open(FS,"<$fsf") ||  die "Can't open $fsf file $!\n";
	open(SS,"<$ssf") ||  die "Can't open $ssf file $!\n";
	open(OS,">$osf") ||  die "Can't open $osf file $!\n";

	printf(OS "# $vers\n");
	printf(OS "# Generated from $fsf and $ssf on $dtstamp\n");
	printf("Merging files $fsf and $ssf\n");
	printf(OS "#\n");

	#copy over first file completely
	$sline="";
	while ($line = <FS>) {
		printf(OS "$line");
		chomp($line);
		$line =~ s/^\s+|\s+$//g;
		@c=split(" ",$line);
		if (scalar(@c) > 0) {
                   if (looks_like_number($c[0])) {
			# dataline - save
			$dimc=scalar(@c);
			@a=[];
			for ($i=0;$i<$dimc;$i++) {
				$a[$i]=$c[$i];
			}
			$sline = $line;
		    }
		}
	}
	close(FS);

	# extract cumulatives from last line

$dima=scalar(@a);
#for ($i=0;$i<$dima;$i++) {
#	printf("a=$a[$i]\n");
#}
#printf("dima = $dima\n");
#printf("saved line = $sline\n");
	
	# Read and process second file
	printf(OS "# merged file - $ssf\n");
	while ($line = <SS>) {
	    	chomp($line);
		$line =~ s/^\s+|\s+$//g;
                @b=split(" ",$line);
                if (scalar(@b) > 0) {
                   if (looks_like_number($b[0])) {
                        # not a header or comment line
			$dimb = scalar(@b);
			if ($dima != $dimb) {
				printf("unmatched dimensions $dima,$dimb\n");
				printf("$line\n");
				exit(0);
			}
			printf(OS "$b[0]");
			for ($i=1;$i<scalar(@b);$i++) {
				if (($i % 2) == 0) {
					# cumulative - add in value of last line of first file
					$b[$i]=$b[$i]+$a[$i];
					$b[$i]=sprintf("%8.6e",$b[$i]);
				}
				printf(OS "  $b[$i]");
			}
			printf(OS "\n");
                   }
                }
        }
        close(SS);
	close(OS);
}

