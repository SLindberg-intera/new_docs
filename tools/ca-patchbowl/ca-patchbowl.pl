#!/usr/bin/perl -w
# ca-patchbowl.pl
# 
# Created by MDWilliams, INTERA 2-15-2018
#	Closes off holes in CC lower silt that
#	allows for CC sand to directly contact CC gravels
#

$iplt = shift @ARGV;
$izone = shift @ARGV;
$mat1 = shift @ARGV;
$mat2 = shift @ARGV;
$mat3 = shift @ARGV;
$ozone = shift @ARGV;

print("Mat1 = $mat1, Mat2 = $mat2\n");

open(IP,"<$iplt") || die "Can't open $iplt file $!\n";
open(IZ,"<$izone") || die "Can't open $izone file $!\n";
open(OZ,">$ozone") || die "Can't open $ozone file $!\n";


# scan STOMP Plot File
# find time line
$flag = 1;
while($flag) {
	$line = <IP>;
	chomp($line);
	if (substr($line,0,4) eq "Time") {
		$timeline=$line;
		$flag = 0;
	}
}

#extract year 
@a=split(" ",$timeline);
print("$a[7]\n");
@a=split(",",$a[7]);
$yr=sprintf("%.3f",$a[0]);

# find number of nodes
$flag = 1;
while($flag) {
	$line= <IP>;
	chomp($line);
	  if (substr($line,0,7) eq "Number ") {
		@a = split(" = ",$line);
		$nx = $a[1];
		$line= <IP>;
        	chomp($line);
		@a = split(" = ",$line);
                $ny = $a[1];
		$line= <IP>;
        	chomp($line);
		@a = split(" = ",$line);
                $nz = $a[1];
                $line= <IP>;
                chomp($line);
                @a = split(" = ",$line);
                $xo = $a[1];
                $line= <IP>;
                chomp($line);
                @a = split(" = ",$line);
                $yo = $a[1];
                $line= <IP>;
                chomp($line);
                @a = split(" = ",$line);
                $zo = $a[1];
		# skip blank before data
		$line = <IP>;
		$flag=0;
	}
}
print(" nx,ny,nz = $nx,$ny,$nz\n");
close(IP);

# load zonation file
$p=0;
while ($line = <IZ>) {
	chomp($line);
	$line =~ tr/ //s;
	$line =~ s/^\s+//;
	@a = split(" ",$line);
	for ($i=0;$i<scalar(@a);$i++) {
		$za[$p]=$a[$i];
		$p++;
	}
}
close(IZ);
print("Zone file count = $p\n");

$ijk = 0;
for ($k=0;$k<$nz;$k++) {
	for ($j=0;$j<$ny;$j++) {
		for ($i=0;$i<$nx;$i++) {
			$p = ($i+ ($j*$nx) + ($k*$nx*$ny));
			$z[$i][$j][$k] = $za[$p];
			if ($za[$p] < 0) {
				print("P = $p, IJK=$i,$j,$k az=$za[$p]\n");
			}
	
			$ijk++;
		}
	}
}
print("IJK count = $ijk\n");
$pcnt = 0;

for ($k=0;$k<$nz;$k++) {
        for ($j=0;$j<$ny;$j++) {
                for ($i=0;$i<$nx;$i++) {
			if ($z[$i][$j][$k] == $mat1) {
				# check bottom
				if ($k > 0) {
					if (($z[$i][$j][$k-1] != $mat1) && ($z[$i][$j][$k-1] != $mat2) 
					&& ($z[$i][$j][$k-1] == $mat3)) {
						$z[$i][$j][$k-1] = $mat2;
						$pcnt++;
					}

				}
				# check front
                                if ($j > 0) {
                                        if (($z[$i][$j-1][$k] != $mat1) && ($z[$i][$j-1][$k] != $mat2)
					&& ($z[$i][$j-1][$k] == $mat3)) {
                                                $z[$i][$j-1][$k] = $mat2;
                                                $pcnt++;
                                        }

                                }
 				# check back
                                if ($j < $ny-1) {
                                        if (($z[$i][$j+1][$k] != $mat1) && ($z[$i][$j+1][$k] != $mat2)
					&& ($z[$i][$j+1][$k] == $mat3))  {
                                                $z[$i][$j+1][$k] = $mat2;
                                                $pcnt++;
                                        }

                                }
				# check east
                                if ($i < $nx-1) {
                                        if (($z[$i+1][$j][$k] != $mat1) && ($z[$i+1][$j][$k] != $mat2)
					&& ($z[$i+1][$j][$k] == $mat3)) {
                                                $z[$i+1][$j][$k] = $mat2;
                                                $pcnt++;
                                        }

                                }
				# check west
                                if ($i > 0) {
                                        if (($z[$i-1][$j][$k] != $mat1) && ($z[$i-1][$j][$k] != $mat2)
					&& ($z[$i-1][$j][$k] == $mat3)) {
                                                $z[$i-1][$j][$k] = $mat2;
                                                $pcnt++;
                                        }
                                }
			}
                }
        }
}
print("Number of Patched Materials = $pcnt\n");
$lcnt=0;
for ($k=0;$k<$nz;$k++) {
        for ($j=0;$j<$ny;$j++) {
                for ($i=0;$i<$nx;$i++) {
			printf(OZ "%4d",$z[$i][$j][$k]);
			$lcnt++;
			if ($lcnt == 20) {
				printf(OZ "\n");
				$lcnt = 0;
			}
		}
	}
}

close(OZ);

