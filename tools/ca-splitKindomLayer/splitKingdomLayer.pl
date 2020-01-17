#!/usr/bin/perl -w
#
# splitKingdomLayer.pn
# Created by MDWilliams, 2-28-2019
# Program slips a layer into 2 layers based on being inside or outside a polygon
#
# Arguments:
# 	input kingdom layer
# 	polygon
# 	inside Kingdom layer to create
# 	Outside Kingdom layer to create
#


$ikn = shift @ARGV;
$ipn = shift @ARGV;
$okin = shift @ARGV;
$okon = shift @ARGV;

open(IK,"<$ikn") || die "Can't open $ikn file $!\n";
open(IP,"<$ipn") || die "Can't open $ipn file $!\n";
open(KI,">$okin") || die "Can't open $okin file $!\n";
open(KO,">$okon") || die "Can't open $okon file $!\n";

# load polygon (Kingdom format)
# Skip header (7 Lines)
for ($i=0;$i<7;$i++) {
	$line = <IP>;
}
# get number of coords
$line = <IP>;
chomp($line);
$npt = int($line);
$lcnt=5;  # 5 pairs per line
for ($i=0;$i<$npt;$i++) {
	if ($lcnt == 5) {
		$line = <IP>;
		chomp($line);
		@a = split(" ",$line);
		$lcnt=0;
	}
	$px[$i]=$a[$lcnt*2];
	$py[$i]=$a[($lcnt*2)+1];
	$lcnt++;
}
printf("Polygon npt = $npt\n");

# read Kingdom CSV file and write lines into either inside or outside files
# depending on whether the coordinate is within the polgyon

while ($line = <IK>) {
	chomp($line);
	@a = split(",",$line);
	$x=$a[0];
	$y=$a[1];
#	printf("x,y = $x,$y\n");
	if (within($x,$y)) {
		# inside
		printf(KI "$line\n");
#		printf(KO "$x,$y,-99999\n");
	} else {
		# outside
		printf(KO "$line\n");
#		printf(KI "$x,$y,-99999\n");
	}
}

close(IK);
close(IP);
close(KI);
close(KO);
exit(0);


# Subroutines
# *****************************************************************
# 	within
#
#		Dertermines if a point is
#		inside a polygon defined by a variable
#		number of points.
#
#		This logic was stolen from CFEST subroutines
#		written by Larry Gerhardstein (PNL)
#
#Arguments:
#
#	npt = # of coordinate pairs in the polygon
#	x,y = arrays containing coorinates of the polygon vertices
#	xc,yc = coordinate of the point to be checked
#
#	within = 0: point is outside of region
#	within != 0: point is within region
#

sub gsgn
# float gsgn(a1,a2)
# float a1,a2;
{
	my ($a1,$a2) = @_;

	if ($a2 >= 0) {
        	return(abs($a1));
	 } else {
        	return(-abs($a1));
	}
}

sub within
# int within(npt,px,py,xc,yc) 
# note: npt,px,py are global in this version
#int npt;
#float px[],py[];
#float xc,yc;
{
#int i,ic,ntime,hflag;
#float x1,x2,y1,y2,sx1,sx2,sy1,sy2;
#float m,b;
#float xdiff,ydiff,ptol;
#float dx;

	my ($xc,$yc) = @_;
# printf("in within: npt=$npt,$px[0],$py[0],$xc,$yc\n");
$ptol=1E-7;
$ic=0;
$ntime=0;
$x1=$px[0]-$xc;
$y1=$py[0]-$yc;
if (($x1==0.0) && ($y1==0.0)) {
	return(1);
}

#/* check to see if point is on perimeter of zone */
        for ($i=0;$i<$npt-1;$i++) {
#        /* calculate point/slope eqn of line segment */
#	    /* check if dx = 0 -> infinite slope */
	    $dx=$px[$i+1]-$px[$i];
	    if ($dx == 0.0) {
#		/* infinite slope logic */
		$xdiff = $xc-$px[$i];
		if ($xdiff < 0.0) {
			$xdiff=-$xdiff;
		}
		if ($xdiff < $ptol) {
		        if ((($yc >= $py[$i]) && ($yc <= $py[$i+1])) || (($yc <= $py[$i]) && ($yc >= $py[$i+1]))) {
#/*                                printf("within - on perimeter with infinite slope\n"); */
                                return(1);
			}
		}
	    } else {
                $m = ($py[$i+1]-$py[$i])/($px[$i+1]-$px[$i]);
                $b = $py[$i]-($m*$px[$i]);
		$ydiff=$yc-(($m*$xc)+$b);
		if ($ydiff < 0.0) {
			$ydiff=-$ydiff;
		}
                if ($ydiff < $ptol) {
#                        /* on perimeter - make sure its within line segment limits */
                        if ((($xc >= $px[$i]) && ($xc <= $px[$i+1])) || (($xc <= $px[$i]) && ($xc >= $px[$i+1]))) {
#/*				printf("within - on perimeter\n");
#				printf("i=%d,m=%f,b=%f\n",$i,$m,$b);  */
                                return(1);
			}
                }
	    }
        }


$sx1=gsgn(1.0,$x1);
$sy1=gsgn(1.0,$y1);

#/* main loop */
$i=1;
$hflag=0;
$ntime=0;
while($i<$npt) {
	if ($hflag==0) {
		$x2=$px[$i]-$xc;
		$y2=$py[$i]-$yc;
		$ntime=0;
	} else {
		$hflag=0;
	}

	if (($x2==0.0) && ($y2==0.0)) {
		return(1);
	}

	$sx2=gsgn(1.0,$x2);
	$sy2=gsgn(1.0,$y2);

	if (($sx1!=$sx2) || ($sy1!=$sy2)) {
#		/* starting and ending points are in
#		   different quadrants */
		if ($sy1==$sy2) {
			if ($sx1==$sy2) {
#				/* moving counterclockwise */
				$ic++;
			} else {
#				/* moving clockwise */
				$ic--;
			}
		} else { 
		   if ($sx1==$sx2) {
			if ($sx1==$sy1) {
#				/* moving clockwise */
				$ic--;
			} else {
#				/* moving counterclockwise */
				$ic++;
			}
		   } else {
#	               /* special case - new quadrant is oblique to old
#        		  cut step size in half and try again */
			$hflag=1;
                	$x2 = $x1+($x2-$x1)/2.0;
	                $y2 = $y1+($y2-$y1)/2.0;
               		$ntime++;
               		if ($ntime > 15) {
				return(1);
			}
                   }
		}
	}

	if ($hflag==0) {
	        $i++;
	        $x1=$x2;
	        $y1=$y2;
	        $sx1=$sx2;
	        $sy1=$sy2;
	        if ($ntime!=0) {
	                $ntime=0;
	                $i--;
	        }
	}
}	
return($ic);
}

# ******************* end subroutines
