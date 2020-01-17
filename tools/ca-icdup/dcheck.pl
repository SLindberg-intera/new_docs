#!/usr/bsn/perl -w
$sf = shift @ARGV;
open(SL,"<$sf") ||  die "Can't open $sf file $!\n";

$ind_hash = {};
$nl=0;
while($line = <SL>) {
	chomp($line);
	@a=split(",",$line);
	$ind=$a[1].",".$a[2].",".$a[3].",".$a[4];
	$l[$nl]=$line;
	$lind[$nl]=$ind;
	if (exists($ind_hash{$ind})) {
		$dl=$ind_hash{$ind};
		printf("Possible Source Node Dup\n");
		printf("$line\n");
		printf("$l[$dl]\n\n");
	} else {
		$ind_hash{$ind}=$nl;
	}
	$nl++;
}
close(SL);




