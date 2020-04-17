#!/usr/bsn/perl -w
# $RCSfile$ $Date$ $Author$ $Revision$
# ca-src2stomp.pl
# Created by MDWilliams, 8-8-2017
#   Maps SAC Sources (CA-Ref-A_inv1.res) using waste site geometry 
#   (ehsit ArcGIS shapefile converted to csv) onto a STOMP grid.  
# Change-LOG
#    Ver 1.3 8/25/2017 MDWilliams
# -	fixed source bug where need a zero when sources restart after a period 
#	of zeros
# -	Added option for selected only a few solutes (Sr-90,I-129,Tc-99, U-238, U-235, U-233)	 
#	see input file for flag
# -	Stuff ...
#   Version 1.6 - sorting grid blocks based on percentage of area of intersection instead of area 
#          	  This is important when source covers non-uniform grid spacing.
#   Version 1.7 - added output of total liquid and activities by waste site and by year
#		  csv format for plotting (will have an excell template)
#   Version 1.8 - Fixed bug that was messing up yearly data (totals were OK).
#   Version 1.9 - less boneheaded algorythm to shorten node list for area limited case.  
#		  Should permit better lumping of nodes in a source cards (fewer cards needed).
#   Version 2.0 - scaling sources to gridblock area - for cases where waste sites span different
#                 grid spacing regions.
#   Version 2.1 - bug - wasn't checking to see if node was outside clip region - could still be in a
#                 waste site (but outside clip poly)
#   Version 2.2 - bug - not using clipped area of waste sites for area limited.
# 
#   Version 2.3 - bug - Corrected fractional source value in card comments
#
#   Version 2.42 - Assorted fixes:
#			- writing only area limited nodes to log file if that option is selected
#			- adding sums to second column of csv file
#			- added another set of sums sorted by liquid volume
#			- added another set of annual sums sorted by year
#   Version 2.5	-  Added water sources that have no radionucludes (from a separate file) to
#		   source cards. Note that these sources were attenutated through a 1D 
#		   vadose zone model for use in direct aquifer recharge.  
#		   This should be fixed in the new inventory.
#
#   Version 3.0 - Multipolygon waste sites.  Unwrapped and calculating fractional sources for each polygon.
#		  Using grid area for calculating fractional sources.
#
#   Version 3.1 - added some spaces after = in grid card comments (areas)
#
#   Version 3.2 - Added multi polygon to csv file
#
#   Version 4.0	-  Centering sources for trench-like waste sites for area limited - sort of
#   Version 5.1 - Now linked to SIM Inventory (different format than SAC), we still need to supplement with SAC water Sources (non rad releases). 
#          Changed ctl file format (explicitly list rads).
#   Version 5.3 - patched bug where it was choking on inventory with no liquid volume.
#
#   Vserion 5.4 - changed m3 to m^3 (from SIM2 Inventory), added # to first three lines of source card file,
#                 moved number of source cards to correct position
#   Version 5,5 - Changed Uppercase Liquid in SIM to lower case
#
#   Version 5.6 - Not outputing solids (waiting for source terms), Writing out only nodes that have sources in new log file
#   
#   Version 5.7 - Don't always go for one node over the site area.  Below or Above - whichever is closer.
#
#   Version 5.8 - New SIMV2 Inventory file (header is slighly different).  Allowing Liquid/Solid sites in.
#
#   Version 6.0 - Started using IPP (Inventory Preprocessor Output File - Appendix F with cleanup, rerouting liquid
#                 Sites, Solid Waste Releases.  Note: This Version changes the ctl file format (No Solid and Yes Solid)
#		  Format of inventory file changed.  Now there are two site names, one for SIM and on for CA.
#   Version 6.1 - Additionally,  Need to merge multiple lines with data for same year for a site. Othersize other
#	 	  Inventory reprocessing isn't needed.
#                 Added another option for solids only
#
#   version 6.2 - Removed SAC Liquid only inventory
#
#   version 6.3 - Fixed bug to output liquid for liquid/Solid site
#
#   version 6.4 - treating solid waste series as releases
#
#   version 6.5 - don't limit area for ancillary equipment sites (surround tank farms)
# 
#   version 6.7 - bug fixed for skipping initial zero on series
#
#   version 6.8 - got no solids option working
#
#   version 6.9 - added source node list output for postprocessing
#   
#   version 7.0 - fixed bug with partitioning multi-polygon sources where one
#		  or more is clipped by a boundary
#
#   version 7.1 - extra header lines in inventory
#
#   version 7.2 - added ZTop min and max to waste site headers
#
#   version 7.3 - fixed source years to stomp alternating from fixed to float
#
#   version 7.4 - New format for zone file and changed ctl file format (added zone name)
#
#   version 7.5 - Removing dups from ANCs.  wastesite outline leaving some holes or other non-tank sources.
#
#   version 7.6 - adding more date entries for 10,000 year CA run in the summary file.  Integrating solid mass over those periods
#
#   version 7.7 - Bug fix - leaving some -1 ANC nodes. Also commented out unused variables.
#   
#   version 7.8 - fixing totals in -sum.csv table (errors in site with both solid and liquid wastes), added a table file output


use Data::Dumper;
use Math::Geometry::Planar;
use Math::Polygon::Calc;

$vers="src2stomp 4/2/2020 Ver 7.8 by MDWilliams, Intera Inc";

$cf = shift @ARGV;	# get control file
# control file format
# STOMP Grid file name (surface IJ)
# STOMP Grid .top file (K of uppermost Active IJ)
# Polygon file for sources (to clip domain if needed) or "Grid" keyword
# name of zone in polygon file (new in version 7.4)
# ehsit ascii csv file (converted from shapefile)
# source term file (SAC 2006 for now - CA-Ref-A_inv1.res)
# "Solid" or "No Solid" or "Only Solid"
# "Limited" or "Unlimited" (based on Area of nodes in polygon)
# Output file prefix
# # of rads
# following line repeated for number of lines:
# radname [matched to inventory file], newname  (example: Uranium-238, U-238)

open(C,"<$cf") ||  die "Can't open $cf file $!\n";
$sgrid=<C>;
chomp($sgrid);
$gtop=<C>;
chomp($gtop);
$zfname=<C>;
chomp($zfname);
$zname=<C>;
chomp($zname);
$ehsit=<C>;
chomp($ehsit);
$radinv=<C>;
chomp($radinv);
$solidflag =<C>;
chomp($solidflag);
$solidflag = lc($solidflag);
if (($solidflag ne "no solid") && ($solidflag ne "solid") &&  ($solidflag ne "solid only")) {
	printf("Error = Invalid Solid Flag = $solidflag\n");
	exit(0);
}
$limarg=<C>;
chomp($limarg);
$limarg =~ s/[\r\n]+$//;
if (lc($limarg) eq "limited") {
	$lim=1;
} elsif (lc($limarg) eq "unlimited") {
	$lim=0;
} else {
	printf("Invalid Limited Argument = .$limarg.\n");
	exit(0);
}
$outpref=<C>;
$outpref =~ s/[\r\n]+$//;
chomp($outpref);
$ninc=<C>;
chomp($ninc);
for ($i=0;$i<$ninc;$i++) {
	$line=<C>;
	chomp($line);
	# remove leading and trailing white spaces
	$line =~ s/^\s+|\s+$//g;
	$inc[$i]=$line;
	$inccol[$i]=-1;
}
close(C);

$outlog=$outpref.".log";
$outlogact=$outpref."-active.log";
$outcard=$outpref.".card";
$outrnode=$outpref.".ref";
$outsum=$outpref."-sum.csv";
$outtbl=$outpref."-table.csv";
$outsrclist=$outpref."-srclist.csv";
$tcard = "toss.card";

open(IG,"<$sgrid") || die "Can't open $sgrid file $!\n";
open(TP,"<$gtop") || die "Can't open $gtop file $!\n";
open(SG,"<$ehsit") || die "Can't open $ehsit file $!\n";
open(SR,"<$radinv") || die "Can't open $radinv file $!\n";
open(OL,">$outlog") || die "Can't open $outlog file $!\n";
open(OA,">$outlogact") || die "Can't open $outlogact file $!\n";
open(TC,">$tcard") || die "Can't open $tcard file $!\n";
open(OC,">$outcard") || die "Can't open $outcard file $!\n";
open(SN,">$outrnode") || die "Can't open $outrnode file $!\n";
open(OS,">$outsum") || die "Can't open $outsum file $!\n";
open(OT,">$outtbl") || die "Can't open $outtbl file $!\n";
open(OSL,">$outsrclist") || die "Can't open $outsrclist file $!\n";


# load ij surface grid - create elements (polys)
$line = <IG>;
chomp($line);
@a=split(" ",$line);
$nsx=$a[0];
$nsy=$a[1];
$nx=$nsx-1;
$ny=$nsy-1;
print "NSX NSY = ",$nsx," ",$nsy,"\n";
print "NX NY = ",$nx," ",$ny,"\n";
for ($j=0;$j<$nsy;$j++) {
	for ($i=0;$i<$nsx;$i++) {
		$line = <IG>;
		chomp($line);
		@a=split(" ", $line);
		$ti=$a[0]-1;
		$tj=$a[1]-1;
		$sx[$ti][$tj]=$a[2];
		$sy[$ti][$tj]=$a[3];
	}
}
close(IG);
# Calculate Node xy from surfaces
#for ($j=0;$j<$ny-1;$j++) {
#	for ($i=0;$i<$nx-1;$i++) {
#		$x[$i][$j]=(($sx[$i][$j]+$sy[$i+1][$j])/2.0);
#		$y[$i][$j]=(($sy[$i][$j]+$sy[$i][$j+1])/2.0);
#	}
#}

# build ploygon elements from stomp surfaces
$nc=0;
for ($j=0;$j<$nsy-1;$j++) {
	for ($i=0;$i<$nsx-1;$i++) {
	    $gpoly = Math::Geometry::Planar->new;
	    $gpoly->points([[$sx[$i][$j],$sy[$i][$j]],
			    [$sx[$i+1][$j],$sy[$i+1][$j]],
			    [$sx[$i+1][$j+1],$sy[$i+1][$j+1]],
			    [$sx[$i][$j+1],$sy[$i][$j+1]]]);
	    $ccx[$nc]=($sx[$i][$j]+$sx[$i+1][$j])/2.0;
	    $ccy[$nc]=($sy[$i][$j]+$sy[$i][$j+1])/2.0;
	    $gpoly_area[$nc]=$gpoly->area;
 	    $gpc_gpoly[$nc] = $gpoly->convert2gpc([$gpoly]);
	    $nc++;
	}
}

# load top file
for ($j=0;$j<$nsy-1;$j++) {
	for ($i=0;$i<$nsx-1;$i++) {	
		$line=<TP>;
		chomp($line);
		@a=split(" ",$line);
		$top[$a[0]][$a[1]]=$a[2];
	}
}
close(TP);


# load clip zone file (if != none)
if ($zfname=~/none/i) {
	$cpx[0]=$sx[0][0];
	$cpy[0]=$sy[0][0];
	$cpx[1]=$sx[$nsx-1][0];
	$cpy[1]=$sy[0][0];
	$cpx[2]=$sx[$nsx-1][$nsy-1];
	$cpy[2]=$sy[$nsx-1][$nsy-1];
	$cpx[3]=$sx[0][0];
	$cpy[3]=$sy[$nsx-1][$nsy-1];
	$cpoly = Math::Geometry::Planar->new;
	$cpoly->points([[$cpx[0],$cpy[0]],[$cpx[1],$cpy[1]],
			[$cpx[2],$cpy[2]],[$cpx[3],$cpy[3]]]);
	$gpc_cpoly = $cpoly->convert2gpc([$cpoly]);
	
} else {
	@ps=[];
	$np=0;
	open(ZF,"<$zfname") || die "Can't open $zfname file $!\n";
	# skip header
	$line = <ZF>;
	$flag = 0;
	while ($line = <ZF>) {
	   if ($flag == 0) {
		# search for zone name
		chomp($line);
		@a=split(",",$line);
		if ($a[0] =~ m/$zname/i) {
			while ($flag == 0) {
				$ps[$np]=[$a[1],$a[2]];
    				$np++;
				$line = <ZF>;
				chomp($line);
				@a = split(",",$line);
				if ((eof(ZF)) || ($a[0] ne '')) {
					$flag = 1;
				}
			}
		}
	    }
	}
	close(ZF);
	$cpoly = Math::Geometry::Planar->new;
        $cpoly->points(\@ps);
        $gpc_cpoly = $cpoly->convert2gpc([$cpoly]);
}

# load ehsit (shapefile of waste sites, converted to csv)
# skip header
$line = <SG>;
$nhsit=0;
@npolys=[];
@mpoly=[];
$nms=0;
$cres = Math::Geometry::Planar->new;
$np=0;
$spolys = Math::Geometry::Planar->new;
$spoly =  Math::Geometry::Planar->new;
$sx=-99999.0;
$sy=-99999.0;
$mpcnt=0;
$pflag=0;
while ($line = <SG>) {
    chomp($line);
    @a =split(",",$line);
    $ra=$a[1]+0.0;
    $rb=$a[2]+0.0;
     if (($a[0] ne '') || (($ra == $sx) && ($rb == $sy))) {
      	if ($np > 0) {
		$spoly = Math::Geometry::Planar->new;
		@tps = @ps;
		$spoly->points(\@tps);
#		$tn = scalar(@tps);
		$ts = $spoly->area;
#		print("Area of $sitname[$nhsit] = $ts, npoints = $tn\n");
#		for ($i=0;$i<$tn;$i++) {
#			print("  $tps[$i][0],$tps[$i][1] \n");
#		}
		if ($mpcnt==0) {
                        $mpoly[$nhsit]=$nhsit;
                        $npolys[$nhsit]=1;
		}
		if (($ra == $sx) && ($rb == $sy)) {
		    if ($mpcnt == 0) {
			$fpoly=$nhsit;
			$mpoly[$nhsit]=$fpoly;
			$mpcnt=1;
		    } else {
			$mpoly[$nhsit]=$fpoly;
			$mpcnt++;
		    }
		    $npolys[$nhsit]=1;
		    $npolys[$fpoly]=$mpcnt;
		    $line = <SG>;
		    if (defined ($line)) {
		    	chomp($line);
    		    	@a =split(",",$line);
    		    	$ra=$a[1]+0.0;
    		    	$rb=$a[2]+0.0;
		    	if ($a[0] eq '') {
				$tcnt=$mpcnt+1;
				$a[0]=$sitname[$fpoly]."-Part".$tcnt;
				$npolys[$nhsit]=$tcnt;
				$wastename[$nhsit]=$sitname[$fpoly];
				$pflag=1;
				$wname=$wastename[$nhsit];
		    	} else {
				$mpcnt=0;
		    	}
		    }
		} else {
		    $mpcnt=0;
		}
                push @spolys,$spoly;
                $nhsit++;
	} else {
		$npolys[$nhsit]=1;
		$mpoly[$nhsit]=$nhsit;
	}
    	$sitname[$nhsit]=$a[0];
	if ($pflag == 1) {
		$wastename[$nhsit]=$wname;
		$pflag=0;
	} else {
		$wastename[$nhsit]=$a[0];
	}
    	$sx = $ra;
    	$sy = $rb;
    	$np=0;
    	@ps=[];
    } 
    $ps[$np]=[$ra,$rb];
    $np++;
}
close(SG);

for ($p=0;$p<$nhsit;$p++) {
#        printf("\nProcessing $sitname[$p]....");
	$spoly = shift @spolys;
#	@pts = $spoly->points();
#	print Dumper \@pts;
# 	$tn = scalar(@pts);
        $ts = $spoly->area;
#        print("Area = $ts");
        $gpc_spoly = $spoly->convert2gpc($spoly);
        $result = GpcClip("INTERSECTION",$gpc_cpoly,$gpc_spoly);
        @contours = Gpc2Polygons($result);
        if (defined $contours[0]) {
            $polygon_refs = $contours[0]->polygons;
            $polygon_ref  = ${$polygon_refs}[0];
            @pts = @{$polygon_ref};
            $lp = scalar(@pts);
            $cres->points(\@pts);
            $t = $cres->area;
            $msitearea[$nms] = $spoly->area;		
            $msiteiarea[$nms]=$t;
#           print("Area=$msitearea[$nms], Intersect Area=$msiteiarea[$nms]\n");
#           if ($msitearea[$nms] != $msiteiarea[$nms]) {
#               print(" areas not equal\n");
#           }
#	    print("\nbefore centroid call: Area=$t\n");
#            for ($i=0;$i<$lp;$i++) {
#                   print("  $pts[$i][0],$pts[$i][1] \n");
#            }

#	     printf("before centroid call on $nms ...");
#	     ($xcent[$nms],$ycent[$nms]) = polygon_centroid(@pts);
#	     printf("xycent = $xcent[$nms], $ycent[$nms]\n");

#            $msitecent[$nms]=$cres->centroid;
#            print("centroid = $msitecent[$nms][0], $msitecent[$nms][1]\n");

#	     printf("before bbox call on $p,$nms,$sitname[$p] ...");
	     ($xmin,$ymin,$xmax,$ymax) = polygon_bbox(@pts);
#	     printf("bbox = $xmin,$ymin,$xmax,$ymax");
	     $xcent[$nms]=($xmin+$xmax)/2.0;
	     $ycent[$nms]=($ymin+$ymax)/2.0;
#	     printf("xycent = $xcent[$nms], $ycent[$nms]\n");

#print("intersection with $sitname[$p], Area= $t, # of points= $lp\n");
#           for ($i=0;$i<$lp;$i++) {
#               print("${$pts[$i]}[0],${$pts[$i]}[1]\n");
#           }
            $msite[$nms]=$sitname[$p];
	    $mwastename[$nms]=$wastename[$p];
            $nn=0;
            $n=0;
#            $mink=999999;
#  	     $maxk=-999999;
            for ($j=0;$j<$nsy-1;$j++) {
                for ($i=0;$i<$nsx-1;$i++) {
                    # is the node in waste site polygon?
                    $gres = GpcClip("INTERSECTION",$gpc_spoly,$gpc_gpoly[$n]);
                    @gcon = Gpc2Polygons($gres);
                    if (defined $gcon[0]) {
                      # is the gridblock in clipped region also?
                      $tgres = GpcClip("INTERSECTION",$gpc_cpoly,$gpc_gpoly[$n]);
                      @tgcon = Gpc2Polygons($tgres);
                      if (defined $tgcon[0]) {
                        $gcon_refs = $gcon[0]->polygons;
                        $gcon_ref  = ${$gcon_refs}[0];
                        @pts = @{$gcon_ref};
                        $cres->points(\@pts);
                        $t = $cres->area;
                        $lp = scalar(@pts);
#                       print("Cell Intersection points:\n");
#                       for ($k=0;$k<$lp;$k++) {
#                               print("${$pts[$k]}[0],${$pts[$k]}[1]\n");
#                       }
                        $msi[$nms][$nn]=$i+1;
                        $msj[$nms][$nn]=$j+1;
                        $msa[$nms][$nn]=$t;
                        $msga[$nms][$nn]=$gpoly_area[$n];
                        $msfa[$nms][$nn]=$t/$gpoly_area[$n];
                        $mscx[$nms][$nn]=$ccx[$n];
                        $mscy[$nms][$nn]=$ccy[$n];
#                        if ($top[$i+1][$j+1] < $mink) {
#                                $mink = $top[$i+1][$j+1];
#                        }
#                        if ($top[$i+1][$j+1] > $maxk) {
#                                $maxk = $top[$i+1][$j+1];
#                        }

                        $nn++;
                    }
                  }
                  $n++;
                }
            }
            $mnn[$nms]=$nn;
#            $mmink[$nms]=$mink;
#	     $mmaxk[$nms]=$maxk;
            $totarea=0.0;
            $totcarea=0.0;
            for ($i=0;$i<$mnn[$nms];$i++) {
                $totarea=$totarea+$msa[$nms][$i];
                $totcarea=$totcarea+$msga[$nms][$i];
            }
            $msitegarea[$nms]=$totcarea;
            $msitenpolys[$nms]=$npolys[$p];
            $msitempoly[$nms]=$mpoly[$p];
            $nms++;
        } else {
#            print("no intersection with $sitname[$p]\n");
        }
   }

# create separate node list that is constrained by site area
# Also - don't limit area for Ancillary Equipment (surrounds tanks)
if ($lim == 1) {
    for ($n=0;$n<$nms;$n++) {
      if (!($msite[$n] =~ m/ANC/i)) {

	#$msite
	#$msitearea[$n]
	#$mnn[$n]
	#$msi[$nms][$nn]=
	#$msj[$nms][$nn]=
	#$msa[$nms][$nn]=
	#$msga[$nms][$nn]=
	undef %areas;
	undef @arear;
	for ($i=0;$i<$mnn[$n];$i++) {
		$areas{$i}=$msfa[$n][$i];
	}
	@arear = sort { $areas{$b} <=> $areas{$a} } keys %areas;
#	$nk=scalar(@arear);
#	for ($i=0;$i<$nk;$i++) {
#	    print("$i $arear[$i] $areas{$arear[$i]}\n");
#	}

#print("Area ranking:$msite[$n], #nodes= $mnn[$n], Source poly area=$msitearea[$n]\n");
# calculate distance to polygon centroids
	for ($i=0;$i<$mnn[$n];$i++) {
		$dx = $mscx[$n][$arear[$i]]-$xcent[$n];
		$dy = $mscy[$n][$arear[$i]]-$ycent[$n];
		$centdist[$i]=sqrt($dx*$dx + $dy*$dy);
	}
# sort duplicate fractional areas based on distance to centroid
	printf("Before sort ... ");
	$tflag=0;
	while ($tflag == 0) {
		$tflag = 1;
		for ($i=0;$i<$mnn[$n]-1;$i++) {
			if ($msfa[$n][$arear[$i]] == $msfa[$n][$arear[$i+1]]) {
				if ($centdist[$i] > $centdist[$i+1]) {
					# swap order
					$ta = $arear[$i];
					$tb = $centdist[$i];
					$arear[$i]=$arear[$i+1];
					$centdist[$i]=$centdist[$i+1];
					$arear[$i+1]=$ta;
					$centdist[$i+1]=$tb;
					$tflag=0;
				}
			}
		}
	}
	printf("After sort\n");	

# get nodes to fill clipped wastesite area
	$ar = 0;
	$ta = 0.0;
	for ($i=0;$i<$mnn[$n];$i++) {
	    	$testarea = $ta+$msga[$n][$arear[$i]];
		if ($testarea > $msiteiarea[$n]) {
			# find out which is closer
			$below=$ta-$msiteiarea[$n];
			$above=$testarea-$msiteiarea[$n];
			if ((abs($below) >= (abs($above))) || ($ar == 0)) {
				# go for one more node
				$ta=$testarea;
				$ar++;
			}
			last;
		} else {
		   $ta=$testarea;
		   $ar++;
		}
	}
##	# replace all nodes with these based on ranking (potentially shorter);

	if ($ar < $mnn[$n]) {
#		# move shorter list to temp location
#		for ($i=0;$i<$ar;$i++) {
#			$nn=$arear[$i];
#			$tmsi[$i]=$msi[$n][$nn];
#			$tmsj[$i]=$msj[$n][$nn];
#			$tmsa[$i]=$msa[$n][$nn];
#			$tmsga[$i]=$msga[$n][$nn];
#		}
#		# move shorter list back into main arrays
#		for ($i=0;$i<$ar;$i++) {
#			$msi[$n][$i]=$tmsi[$i];
#			$msj[$n][$i]=$tmsj[$i];
#			$msa[$n][$i]=$tmsa[$i];
#			$msga[$n][$i]=$tmsga[$i];
#		}
#
		# new method - compress list, but maintain original order
# print("Compressing sources for area limited list $msite[$n], $n, $mnn[$n], $ar, $msitegarea[$n]\n");
		$ntm=0;
		for ($j=0;$j< $mnn[$n];$j++) {
			# check to see if this node is in the area limited list
			for ($i=0;$i<$ar;$i++) {
				if ($j == $arear[$i]) {
					# yup move to temp
					$tmsi[$ntm]=$msi[$n][$j];
                       			$tmsj[$ntm]=$msj[$n][$j];
                                        $tmscx[$ntm]=$mscx[$n][$j];
                                        $tmscy[$ntm]=$mscy[$n][$j];
                		       	$tmsa[$ntm]=$msa[$n][$j];
		                       	$tmsga[$ntm]=$msga[$n][$j];
					$ntm++;
				}
			}
		}
		if ($ntm != $ar) {
			print("SERIOUS ERROR - EXTRACTING LIMITED LIST\n");
		}
		$msitegarea[$n]=0;
		for ($j=0;$j<$ntm;$j++) {
			$msi[$n][$j]=$tmsi[$j];
                	$msj[$n][$j]=$tmsj[$j];
			$mscx[$n][$j]=$tmscx[$j];
			$mscy[$n][$j]=$tmscy[$j];
                	$msa[$n][$j]=$tmsa[$j];
                	$msga[$n][$j]=$tmsga[$j];
			$msitegarea[$n]+=$msga[$n][$j];
		}
		$mnn[$n]=$ntm;
	    }
	}
     }  
}

# remove duplicates from ANC Sites
for ($n=0;$n<$nms;$n++) {
  if ($msite[$n] =~ m/ANC/i) {
	printf("\nProcsessing ANC = $msite[$n], #nodes = $mnn[$n]\n");
        #$mnn[$n]
        #$msi[$nms][$nn]=
        #$msj[$nms][$nn]=
        #$msa[$nms][$nn]=
        #$msga[$nms][$nn]=
	$ndup=0;
	for ($j=0;$j<$mnn[$n];$j++) {	
	    for ($c=0;$c<$nms;$c++) {
		if ($c != $n) {
		    for ($cj=0;$cj<$mnn[$c];$cj++) {
			if (($msi[$n][$j] == $msi[$c][$cj]) && ($msj[$n][$j] == $msj[$c][$cj])) {
			    # xy match - remove ANC node
			    $ndup++;
			    $msi[$n][$j]=-1;
			}
		    }

		}
	    }
	}
	if ($ndup!=0) {
	# compress list
	  $ar=0;
	  $msitegarea[$n]=0;
          for ($j=0;$j<$mnn[$n];$j++) {
	     if ($msi[$n][$j]==-1) {
		$ar++;
	     } else {
                $msi[$n][$j-$ar]=$msi[$n][$j];
                $msj[$n][$j-$ar]=$msj[$n][$j];
                $mscx[$n][$j-$ar]=$mscx[$n][$j];
                $mscy[$n][$j-$ar]=$mscy[$n][$j];
                $msa[$n][$j-$ar]=$msa[$n][$j];
                $msga[$n][$j-$ar]=$msga[$n][$j];
                $msitegarea[$n]+=$msga[$n][$j];
	      }
            }
            $mnn[$n]=$mnn[$n]-$ar;
	}
	if ($ar != $ndup) {
		printf("Error - ANC compression failure $ndup, $ar\n");
	}
	printf("Done Procsessing ANC = $msite[$n], #nodes = $mnn[$n]\n");
    }
}


# recakc mink and maxk
for ($n=0;$n<$nms;$n++) {
            $mink=999999;
            $maxk=-999999;
            for ($i=0;$i<$mnn[$n];$i++) {
                  $ti=$msi[$n][$i];
                  $tj=$msj[$n][$i];
                  if ($top[$ti][$tj] < $mink) {
                          $mink = $top[$ti][$tj];
                  }
                  if ($top[$ti][$tj] > $maxk) {
                          $maxk = $top[$ti][$tj];
                  }
	    }
	    $mmink[$n]=$mink;
	    $mmaxk[$n]=$maxk;
}

 
#print("After compressing sources for area limited list $n, $mnn[$n], $ar, $msitegarea[$n]\n");
#for ($j=0;$j<$ntm;$j++) {
#	print("($msi[$n][$j], $msj[$n][$j]) ");
#}
#print("\n");
# Write out log file - nodes selected for waste site (this shows all waste sites - even if no inventory/volume)

for ($n=0;$n<$nms;$n++) {
     	printf(OL "$msite[$n] Areas: %10.1f, %10.1f, %10.1f, $mmink[$n] $mnn[$n]\n",
	$msitearea[$n],$msiteiarea[$n],$msitegarea[$n]);
	for ($j=0;$j<$mnn[$n];$j++) {
		printf(OL "   [$msi[$n][$j],$msj[$n][$j]] [$mscx[$n][$j],$mscy[$n][$j]]\n");
	}
}

# Calculate percentage of area for multipolygon waste site
for ($n=0;$n<$nms;$n++) {
	$msitefract[$n]=0.0;
}
for ($n=0;$n<$nms;$n++) {
	if ($msitefract[$n] == 0.0) {
	    if ($msitenpolys[$n]==1) {
		$msitefract[$n]=1.0;
	    } else {
		# get all polys linked to this
		$tpolys=$msitenpolys[$n];
		$mp = $msitempoly[$n];
		$totarea=0.0;
		$pcnt=0;
		for ($n1=0;$n1<$nms;$n1++) {
			if ($msitempoly[$n1]==$mp) {
				$totarea=$totarea+$msitearea[$n1];
				$pcnt++;
			}
		}
		if ($tpolys != $pcnt) {
			print("Error in mpoly fractional area count $msite[$n]: $tpolys, $pcnt\n");
		}
		for ($n1=0;$n1<$nms;$n1++) {
			if ($msitempoly[$n1]==$mp) {
				$msitefract[$n1]=$msitearea[$n1]/$totarea;
			}
		}

	    }
	}
}
# rank nodes based on distance to centroid
#for ($m=0;$m<$nms;$m++) {
#	$md=1E+20;
#	for ($n=0;$n<$mnn[$m];$n++) {
#		$dx = $msitecent[$m][0] - $x[$msi[$m][$n]][$msj[$m][$n]];
#		$dy = $msitecent[$m][1] - $y[$msi[$m][$n]][$msj[$m][$n]];
#		$msitedist[$m][$n] = sqrt(($dx*$dx) + ($dy*$dy));
#		if ($msitedist[$m][$n] < $md) {
#			$md = $msitedist[$m][$n];
#			$mindisti[$m]=$msi[$m][$n]+1;
#			$mindistj[$m]=$msj[$m][$n]+1;
#		}
#	}
#}

# lump sources into groups (if possible)
for ($m=0;$m<$nms;$m++) {
	# check for adjacent Is or Js (if the other is equal)
	$s=0;
	$nis[$m][0]=$msi[$m][0];
	$nie[$m][0]=$msi[$m][0];
	$njs[$m][0]=$msj[$m][0];
	$nje[$m][0]=$msj[$m][0];
	$nija[$m][0]=$msga[$m][0];
	# only let it lump one direction
	$d=0;
	for ($n=1;$n<$mnn[$m];$n++) {
	    if (($msi[$m][$n] == ($nie[$m][$s]+1)) 
			&& ($msj[$m][$n] == $nje[$m][$s]) 
			&& (($d==0) || ($d==1))
			&& ($msga[$m][$n] == $nija[$m][$s])) {
		$nie[$m][$s]=$msi[$m][$n];
		$d=1;
	    } elsif (($msj[$m][$n] == ($nje[$m][$s]+1)) 
			&& ($msi[$m][$n] == $nie[$m][$s])
			&& (($d==0) || ($d==2))
			&& ($msga[$m][$n] == $nija[$m][$s])) {
		$nje[$m][$s]=$msj[$m][$n];
		$d=2;
	    } else {
	      	$s++;
		$nis[$m][$s]=$msi[$m][$n];
		$nie[$m][$s]=$msi[$m][$n];
		$njs[$m][$s]=$msj[$m][$n];
		$nje[$m][$s]=$msj[$m][$n];
		$nija[$m][$s]=$msga[$m][$n];
		$d=0;
	    }
    	}
	$s++;
#print("First Lump for $msite[$m] s=$s\n");
#for ($i=0;$i<$s;$i++) {
#	print("$nis[$m][$i],$nie[$m][$i],$njs[$m][$i],$nje[$m][$i],$nija[$m][$i]\n");
#}
	# see if any of the groups can be lumped
	$g=0;
	while ($g < $s-1) {
		# check - same I range, J range one level higher
	     	if (($nis[$m][$g] == $nis[$m][$g+1]) &&
		    ($nie[$m][$g] == $nie[$m][$g+1]) &&
		    ($nje[$m][$g]+1 == $nje[$m][$g+1]) &&
		    ($nija[$m][$g] == $nija[$m][$g+1])) {
		    	#print("Found groups to lump!\n");
		    	$nje[$m][$g]++;
			# shuffle groups down
			for ($i=$g+1;$i<$s-1;$i++) {
				$nis[$m][$i] = $nis[$m][$i+1];	
				$nie[$m][$i] = $nie[$m][$i+1];
				$njs[$m][$i] = $njs[$m][$i+1];
				$nje[$m][$i] = $nje[$m][$i+1];
				$nija[$m][$i] = $nija[$m][$i+1];
			}
			$s--;
	    	} else {
			$g++;
		}
	}
	$nse[$m]=$s;
#print("Second Lump for $msite[$m] s=$s\n");
#for ($i=0;$i<$s;$i++) {
#        print("$nis[$m][$i],$nie[$m][$i],$njs[$m][$i],$nje[$m][$i],$nija[$m][$i]\n");
#}

}

# write out STOMP Source Cards - Finally (sheesh)
$cl="#------------------------------------------------------------------\n";
printf(OC "$cl");
printf(OC "# Generated by sim2stomp.pl, MDWilliams, Intera, Inc.\n");
printf(OC "# Version=$vers\n");
$t = time();
$local_time = localtime($t);
printf(OC "# Generated on $local_time\n");
printf(OC "$cl");
printf(OC "~Source Card\n");
printf(OC "$cl");
#
printf(OS "$cl");
printf(OS "# Generated by sim2stomp.pl, MDWilliams, Intera, Inc.\n");
printf(OS "# Version=$vers\n");
printf(OS "# Generated on $local_time\n");
printf(OS "$cl");
#
printf(OT "$cl");
printf(OT "# Generated by sim2stomp.pl, MDWilliams, Intera, Inc.\n");
printf(OT "# Version=$vers\n");
printf(OT "# Generated on $local_time\n");
printf(OT "$cl");

# printf(OC "SEE BOTTOM OF FILE (really, it's easier this way),\n");
# printf(OC "$cl");
$nsrc=0;

# load SIM Inventory
# skip first bunch of lines - info
for ($i=0;$i<11;$i++) {
	$line = <SR>;
}

# load header - 2 lines (units and rads)
$line = <SR>;
chomp($line);
@hr=split(",",$line);
#find year, volume, site, source, and units columns
$nhr=scalar(@hr);
for ($i=0;$i<$nhr;$i++) {
        if (lc($hr[$i]) =~ m/ca site name/) {
                $casitecol = $i;
        } elsif (lc($hr[$i]) =~ m/simv2 site name/) {
#                $sim2sitecol = $i;
        } elsif (lc($hr[$i]) =~ m/source/) {
                $sim2sourcecol = $i;
        } elsif (lc($hr[$i]) =~ m/volume/) {
                $sim2volcol=$i;
        } elsif (lc($hr[$i]) =~ m/discharge/) {
                $sim2timecol = $i;
        } elsif (lc($hr[$i]) =~ m/inventory module/) {
                $sim2modulecol = $i;
        }

}
$ntrad = $nhr - 6;
printf("NTRAD = $ntrad, $line\n");
$nsim2rad=0;
for ($i=0;$i<$ntrad;$i++) {
        # remove any parantheticals (space after name)
        @a = split(" ",$hr[6+$i]);
        $s2r = $a[0];
        # remove leading and trailing spaces
        if (defined $s2r) {
            $s2r =~ s/^\s+|\s+$//g;
            # compare against sumulation rad list - save column for a match
            for ($j=0;$j<$ninc;$j++) {
                if ($s2r eq $inc[$j]) {
                        # save column in slots for rads
                        $inccol[$j]=$i+6;
                        $sim2radname[$j]=$s2r;
                        $nsim2rad++;
                }
            }
        }
}

if ($nsim2rad != $ninc) {
	printf("ERROR! - can't find listed rads in SIM2 line=$line\n");
	exit(0);
}

# second line - get rad/chem Units
$line=<SR>;
chomp($line);
@hu=split(",",$line);
for ($i=0;$i<$ninc;$i++) {
	$sim2solunits[$i]=$hu[$inccol[$i]];
}
$sim2radunits=$hu[6];
if (lc($sim2radunits) =~ m/curies/) {
               $sim2radunits = "Ci";
}
#$sim2chemunits=$hu[22];
$sim2timeunits=$hu[$sim2timecol];
$sim2volunits=$hu[$sim2volcol];


for ($i=0;$i<$ninc;$i++) {
	printf("SIM2 Name=$sim2radname[$i], SIM2 Unit=$sim2solunits[$i], SIM2 Column=$inccol[$i]\n");
}

my %yearh;
my %yearsum;
my %swidh;
$nsws=0;
$fflag=1;
# get first SIM2 record
$line=<SR>;
chomp($line);
while ($fflag) {
    $nyear=0;
    $nrad = 0;
    $ylsum = 0.0;
    @radsum = ();
    @year = ();
    @yrad = ();
    @nyrad = ();
    @yrrad = ();
    %radind = ();
    # load sim inventory
    $flag = 1;
    while ($flag) {
      @yl=split(",",$line);
      $swid=uc($yl[$casitecol]);
      $swid =~ tr/\"//d;
      $swid =~ s/^\s+|\s+$//g;
#	printf("Sim Source: #$swid#");
      $yltype= lc($yl[$sim2sourcecol]);
      $yltype =~ s/^\s+|\s+$//g;
      $ylmodule = lc($yl[$sim2modulecol]);
      $ylmodule =~ s/^\s+|\s+$//g;
#	print("yltype=$yltype ylmodule=$ylmodule\n");
#      while ($flag) {
#	$skipflag = 0;
#	if (($solidflag eq "no solid") && ($yltype =~ m/olid/i)) {
#	  printf("No Solid Option - Skipping $swid, $yltype\n");
#	  $skipflag = 1;
#	} else {
	  # check for duplicate years 
	  $dupyearflag = 0;
	  if ($nyear != 0) {
	    for ($i=0;$i<$nyear;$i++) {
		if ($year[$i] == $yl[$sim2timecol]) {
		    # yes, this is a duplicate year - add to last entry
		    $dupyearflag = 1;
		    $dupyearind = $i;
		    $dupyear = $yl[$sim2timecol];
		    printf("We've got duplicate years for a waste site: $swid, $yl[$sim2timecol]\n");
		}
	     }
	  }  
	  # load up volume and rad data from line for this waste site and year
	  if (lc($yl[$sim2sourcecol])=~ m/series/) {
                $seriesflag = 1;
          } else {
                $seriesflag = 0;
          }

	  if ($dupyearflag == 0) {
		$year[$nyear]=$yl[$sim2timecol];
		if ($seriesflag == 0) {
		    if (!defined $yearh{$year[$nyear]}) {
                       	$yearh{$year[$nyear]} = $year[$nyear];
               	    }
		}
		$yltype= lc($yl[$sim2sourcecol]);
	  }
	  # get volume
          $yltype=~ tr/\"//d;
	  $ylunit = $sim2volunits;
	  if (lc($yltype) =~ m/liquid/) {
		$s2vol = $yl[$sim2volcol];
		if ((!defined $s2vol) || ($s2vol eq "")) {
			$s2vol = 0.0;
		}
	  } else {
		$s2vol = 0.0;
	  }
          $ylsum+=$s2vol;
	  if ($dupyearflag == 1) {
                 $ylval[$dupyearind]+=$s2vol;
	  } else {
		$ylval[$nyear]=$s2vol;
	  }
	  # pick up rads for the sim
	  for ($i=0;$i<$ninc;$i++) {
		$mass=$yl[$inccol[$i]];
#		print("mass = \#$mass\#\n");
		if ((defined $mass) && ($mass ne '')) {
		  if ((($seriesflag==0) && ($mass != 0.0)) || ($seriesflag==1)) {
		    if (exists $radind{$sim2radname[$i]}) {
				$t=$radind{$sim2radname[$i]};
				$radsum[$t]+=$mass;
				if ($dupyearflag == 1) {
					# find year to add mass
					$yflag = 0;
					for ($j=0;$j<$nyrad[$t];$j++) {
					    if (defined $yrrad[$j][$t]) {
						if ($yrrad[$j][$t] == $dupyear) {
                               		    	    $yrad[$j][$t]+=$mass;
						    $yflag = 1;
						}
					    }
					}
					if ($yflag == 0) {
					    $yrad[$nyrad[$t]][$t]=$mass;
                                                   $yrrad[$nyrad[$t]][$t]=$dupyear;
                                                   $nyrad[$t]++;
printf("$swid duplicate years at $dupyear, $yrad[$nyrad[$t]-1][$t], $yrrad[$nyrad[$t]-1][$t], $nyrad[$t], -no existing solute for $t $sim2radname[$i] at that year, appending (check date sequence)\n");
					}
                        	} else {
                                	$yrad[$nyrad[$t]][$t]=$mass;
					$yrrad[$nyrad[$t]][$t]=$year[$nyear];
					$nyrad[$t]++;
				}
		    } else {
			$radname[$nrad]=$sim2radname[$i];
			$radunits[$nrad]=$sim2solunits[$i];
			$radsum[$nrad]=$mass;
			$yrad[0][$nrad]=$mass;
			if ($dupyearflag == 0) {
				$yrrad[0][$nrad]=$year[$nyear];
			} else {
				$yrrad[0][$nrad]=$dupyear;
			}
			$nyrad[$nrad]=1;
			$radind{$sim2radname[$i]}=$nrad;
			$nrad++;
		    }
		  }
		}
	       }
	       if ($dupyearflag == 0) {
	    	  $nyear++;
	       }
#	     }
	     # keep searching for more of the same
	     if ($line = <SR>) {
    		chomp($line);
    		@yl=split(",",$line);
		$newswid=uc($yl[$casitecol]);
		$newswid =~ s/%/&/g;
		$newyltype= lc($yl[$sim2sourcecol]);
       		$newyltype =~ s/^\s+|\s+$//g;
       		$newylmodule = lc($yl[$sim2modulecol]);
       		$newylmodule =~ s/^\s+|\s+$//g;
		if (($newswid ne $swid) || ($newyltype ne $yltype) || (($seriesflag ==1) && ($newylmodule ne $ylmodule))) {
			if (($solidflag eq "no solid") && ($yltype =~ m/olid/i)) {
				# do cleanup - but don't build card
				$nyear=0;
			}
			$flag = 0;
		} 
	     } else {
		$flag = 0;
		$fflag = 0;
	     }
           }
     #}
    # ignore if already exists (inventory file) and don't do qnything if no years of data
#    if (($nyear > 0) && (!defined $swidh{$swid})) {
     if ($nyear > 0) {
      # ignore if solid waste site but rad not selected
      if (!(($seriesflag == 1) && ($nrad == 0))) {
	
	# Check if we have this source in our clipped model domain
	for ($m=0;$m<$nms;$m++) {
	  if (lc($swid) eq lc($mwastename[$m])) {
	      	# Yup! - process source
	        if (!defined $swidh{$msite[$m]}) {
       	         	$swidh{$swid}=$msite[$m];
        	}
		# Output to active log file for plotting selected nodes
	        printf(OA "$msite[$m] Areas: %10.1f, %10.1f, %10.1f, $mmink[$m] $mnn[$m]\n",
	        $msitearea[$m],$msiteiarea[$m],$msitegarea[$m]);
	        for ($j=0;$j<$mnn[$m];$j++) {
	                printf(OA "   [$msi[$m][$j],$msj[$m][$j]] [$mscx[$m][$j],$mscy[$m][$j]]\n");
	        }
		# write out headers to cards
		printf(TC "$cl");
		printf(SN "# Site = $msite[$m]\n");
#		printf(ON "$mindisti[$m],$mindistj[$m],$mmink[$m],\n");
		printf(TC "# Site = $msite[$m]\n");
		printf(TC "# Site Area = %.3f, Clipped Site Area = %.3f, Grid Area = %.3f",
			$msitearea[$m],$msiteiarea[$m],$msitegarea[$m]);
		if ($msitefract[$m] !=1.0) {
			$fract[$m]=$msitefract[$m];
			printf(TC ", $msite[$m] multiple poly fractional source =%.3e",$msitefract[$m]);
 			if ($msitearea[$m] != $msiteiarea[$m]) {
				$fract[$m]=$msitefract[$m]*($msiteiarea[$m]/$msitearea[$m]);
				printf(TC ", ending clipped fractional source = %.3e\n",$fract[$m]);	
			} else {
				printf(TC "\n");
			}
		} elsif ($msitearea[$m] != $msiteiarea[$m]) {
                        $fract[$m]=$msiteiarea[$m]/$msitearea[$m];
                        printf(TC ", fractional source = %.3e\n",$fract[$m]);
		} else {
			printf(TC "\n");
			$fract[$m]=1.0;
		}
#		printf(TC "# Site Centroid (X,Y)=($msitecent[$m][0],$msitecent[$m][1]) 
#					Closest Node=($mindisti[$m],$mindistj[$m]])\n");
		if (lc($yltype) =~ m/liquid/) {
			printf(TC "# Note: liquid site = $yltype\n");
		} else {
			printf(TC "# Note: non-liquid site = $yltype\n");
		}
#		$sitesum{$yltype}{$swid} = $w;
		if ($seriesflag == 0) {
		   $w=$ylsum*$fract[$m];
                   printf(TC "# Total Volume = $ylsum ($w) $ylunit\n");
		   $sitesuml{$yltype}{$msite[$m]} = $w;
		   $sitesum{$yltype}{$msite[$m]} = $w;
		   if ($w > 0) {
		    for ($k=0;$k<$nyear;$k++) {
			$w=$ylval[$k]*$fract[$m];
			printf(TC "#      %.1f $ylval[$k] ($w) $ylunit\n",$year[$k]);
			if (exists $yearsum{$yltype} && defined $yearsum{$yltype}{$year[$k]}) {
			    $yearsum{$yltype}{$year[$k]} += $w;
			} else {
			    $yearsum{$yltype}{$year[$k]} =  $w;
			}
		    }
		   }
		} else {
		  # no liquids for solid waste series

		}


		
#		if (lc($yltype) ne "liquid") {
#			$ylsum=0;
#			for ($k=0;$k<$nyear;$k++) {
#				$ylval[$k]=0;
#			}
#			$nyear=0;
#		}


		for ($t=0;$t<$nrad;$t++) {
			$radinc[$t]=1;
			if ($radsum[$t] > 0) {
			   if ($seriesflag == 0) {
			    $w=$radsum[$t]*$fract[$m];
#			    printf("# $swid Total $radname[$t] $radsum[$t] ($w) $radunits[$t]\n");
			    printf(TC "# Total $radname[$t] $radsum[$t] ($w) $radunits[$t]\n");
			    if ($ninc != 0) {
				$radinc[$t]=0;
				for ($j=0;$j<$ninc;$j++) {
					if (lc($radname[$t]) eq lc($inc[$j])) {
						$radinc[$t]=1;
					}
				}
			    }
#			    $sitesum{$radname[$t]}{$swid} = $w;
			    $sitesuml{$radname[$t]}{$msite[$m]} = $w;
			    $sitesum{$radname[$t]}{$msite[$m]} = $w;
			    for ($k=0;$k<$nyrad[$t];$k++) {
				if ($yrad[$k][$t] > 0) {
				    $w=$yrad[$k][$t]*$fract[$m];
				    printf(TC "#     %.1f $yrad[$k][$t] ($w) $radunits[$t]\n",$yrrad[$k][$t]);
				    if (exists $yearsum{$radname[$t]} && defined $yearsum{$radname[$t]}{$yrrad[$k][$t]}) {
	                            	$yearsum{$radname[$t]}{$yrrad[$k][$t]}+= $w;
				    } else {
					$yearsum{$radname[$t]}{$yrrad[$k][$t]} = $w;
				    }
				}
			    }
		    	 } else {
			    # solid waste release series - recalc totals
                            if ($ninc != 0) {
                                $radinc[$t]=0;
                                for ($j=0;$j<$ninc;$j++) {
                                        if (lc($radname[$t]) eq lc($inc[$j])) {
                                                $radinc[$t]=1;
                                        }
                                }
                            }
			    $tw=0;
                            for ($k=0;$k<$nyrad[$t]-1;$k++) {
                                $c1=$yrad[$k][$t];
                                $c2=$yrad[$k+1][$t];
                                $y1=$yrrad[$k][$t];
                                $y2=$yrrad[$k+1][$t];
                                # mean conc over period
                                $ac=($c2+$c1)/2.0;
                                $dt=($y2-$y1);
                                $tw=$tw+($ac*$dt);
				# setup for year totals in summary file
				$swssyear[$nsws] = $y1;
				$swseyear[$nsws] = $y2;
				$swsmean[$nsws] = ($ac*$dt)*$fract[$m];
				$swsyearlyrate[$nsws]=$ac*$fract[$m];
				$swsrad[$nsws] = $radname[$t];
				$swssite[$nsws] = $msite[$m];
                            	$nsws++;
			    }
                            # overwrite earlier calc's total
                            # sig figs (8)
                            $tw=sprintf("%14.8e",$tw);
                            $radsum[$t]=$tw;
                            $w=$tw*$fract[$m];
                            printf(TC "# Total $radname[$t] $radsum[$t] ($w) $radunits[$t]\n");
	                    $sitesum{$radname[$t]}{$msite[$m]} += $w;
                            for ($k=0;$k<$nyrad[$t];$k++) {
                                    $w=$yrad[$k][$t]*$fract[$m];
                                    printf(TC "#     %.1f $yrad[$k][$t] ($w) $radunits[$t]\n",$yrrad[$k][$t]);
#                                   if (exists $yearsum{$radname[$t]} && defined $yearsum{$radname[$t]}{$yrrad[$k][$t]}) {
#                                      $yearsum{$radname[$t]}{$yrrad[$k][$t]}+= $w;
#                                    } else {
#                                        $yearsum{$radname[$t]}{$yrrad[$k][$t]} = $w;
#                                    }
                            }
                      }
		 }
		}
		printf(TC "# Number of Nodes=$mnn[$m]\n");
		printf(TC "# KTop min and max=, $mmink[$m], $mmaxk[$m]\n");
		printf(TC "$cl");
		# set up aq times
		$nl=0;
		for ($i=0;$i<$nyear;$i++) {
			if ($ylval[$i] > 0) {
				if ($nl>0) {
				   if ($seriesflag == 0) {
					if ($tl[$nl-1] != $year[$i]) {
						$tl[$nl]=$tl[$nl-1];
						$vl[$nl]=0.0;
						$nl++;
                                               	$tl[$nl]=$year[$i];
                                                $vl[$nl]=0.0;
                                                $nl++;

					}
				    }
				}
				$tl[$nl]=$year[$i];
# vl is now volume per area - needed to scale volume for different grid spacing within waste site
				if ($msitegarea[$m] <= 0) {
					printf("Error - zero garea $msite[$m] garea=$msitegarea[$m]\n");
				}
				$vl[$nl]=($ylval[$i]*$fract[$m])/($msitegarea[$m]);
#				$vl[$nl]=($ylval[$i]/$mnn[$m])*$fract[$m];
				$nl++;
				if ($seriesflag == 0) {
					$tl[$nl]=$year[$i]+1;
					$vl[$nl]=$vl[$nl-1];
				$nl++;
				}
			}
		}
		if (($nl>0) && ($seriesflag == 0)){
			# add a zero at end
			$tl[$nl]=$tl[$nl-1];
			$vl[$nl]=0.0;
			$nl++;
		}

		if (lc($yltype) =~ m/liquid/) {
		 for ($g=0;$g<$nse[$m];$g++) {
		  if ($ylsum > 0) {
	    	    if (defined $ylunit) {
			$unit=$ylunit."/year";
		    } else {
			$unit = "1/year";
		    }
 		    printf(TC "Aqueous Volumetric,".
		    	" $nis[$m][$g], $nie[$m][$g],".
			" $njs[$m][$g], $nje[$m][$g],".
			" $mmink[$m], $mmink[$m],".
			" $nl,\n");
		    for ($i=0;$i<$nl;$i++) {
#			    printf(TC "$vl[$i], $msitegarea[$m], $nija[$m][$g]\n");
			    printf(TC "%.1f, year, %12.5e, $unit,\n",$tl[$i],$vl[$i]*$nija[$m][$g]);
		    }
		    $nsrc++;
		    # make site list 
		    for ($i=$nis[$m][$g];$i<=$nie[$m][$g];$i++) {
			for ($j=$njs[$m][$g];$j<=$nje[$m][$g];$j++) {
				printf(OSL "$msite[$m],Aqueous Volumetric,");
				printf(OSL "$i,$j,$mmink[$m],");
				for ($ti=0;$ti<$nl;$ti++) {
					printf(OSL "%.1f,",$tl[$ti]);
				}
				printf(OSL "\n");
			}
		    }
		   }
		 }
		}
		# process rads
		for ($s=0;$s<$nrad;$s++) {
	          $nl=0;
		  if (($radinc[$s]==1) && ($radsum[$s] > 0)) {
		    for ($i=0;$i<$nyrad[$s];$i++) {
			if ((($seriesflag == 0) && ($yrad[$i][$s] > 0)) || ($seriesflag ==1)) {
				if (($nl>0) && ($seriesflag == 0)) {
					if ($tl[$nl-1] != $yrrad[$i][$s]) {
						$tl[$nl]=$tl[$nl-1];
						$vl[$nl]=0.0;
						$nl++;
                                                $tl[$nl]=$yrrad[$i][$s];
                                                $vl[$nl]=0.0;
                                                $nl++;
					}
				}
				$tl[$nl]=$yrrad[$i][$s];
# calc massi/activity per unit area (potential different grid spacing in waste site)
				$vl[$nl]=($yrad[$i][$s]*$fract[$m])/($msitegarea[$m]);
#				$vl[$nl]=($yrad[$i][$s]/$mnn[$m])*$fract[$m];
				$nl++;
				if ($seriesflag == 0) {
					$tl[$nl]=$yrrad[$i][$s]+1;
					$vl[$nl]=$vl[$nl-1];
					$nl++;
				}
			}
		    }
		    if (($nl>0) && ($seriesflag == 0)) {
		       	# add a zero at end
			$tl[$nl]=$tl[$nl-1];
			$vl[$nl]=0.0;
			$nl++;
		   }
		   for ($g=0;$g<$nse[$m];$g++) {
		          $nsrc++;
	    	          if (defined $radunit[$s]) {
				$unit=$radunit[$s]."/".$sim2timeunits;
		          } else {
				$unit = "1/".$sim2timeunits;
		          }
 		    	  printf(TC "Solute, $radname[$s],".
		    		" $nis[$m][$g], $nie[$m][$g],".
				" $njs[$m][$g], $nje[$m][$g],".
				" $mmink[$m], $mmink[$m],".
				" $nl,\n");
		    	 for ($i=0;$i<$nl;$i++) {
		    	printf(TC "%.1f, year, %12.5e, $unit,\n",$tl[$i],$vl[$i]*$nija[$m][$g]);
		    	 }
                    # make site list
                    for ($i=$nis[$m][$g];$i<=$nie[$m][$g];$i++) {
                        for ($j=$njs[$m][$g];$j<=$nje[$m][$g];$j++) {
                                printf(OSL "$msite[$m],$radname[$s],");
                                printf(OSL "$i,$j,$mmink[$m],");
                                for ($ti=0;$ti<$nl;$ti++) {
                                        printf(OSL "%.1f,",$tl[$ti]);
                                }
                                printf(OSL "\n");
                        }
                    }

		   }
	        }
	     }
	 }
	}
      }
    }
}

printf(TC "$cl");
printf(TC "$cl");
# printf(OC "# Number of source cards below (finally)\n");
printf(OC "$nsrc,\n");
printf(OC "$cl");

# copu TC over to OC
close(TC);
open(TC,"<$tcard") || die "Can't open $tcard file $!\n";
while ($line = <TC>) {
	printf(OC $line);
}
close(TC);
close(OC);
close(OSL);

# generate sorted csv file for plotting

# Example 1 - turn into 1D Array
# my @flatunsort;
# while (($stype,$sitename) = each(%sitesum)) {
# 	while (($sitename,$total) = each(%$sitename)) {
# 		push(@flatunsort,[$stype,$sitename,$sitesum{$stype}{$sitename}]);
# 	}
# }
# my @flatsort = sort { $$b[0] cmp $$a[0] || $$b[2] <=> $$a[2] } @flatunsort;
# print join("\n", map { join(" ", @$_) } @flatsort), "\n";

# print "\n\n";

# undef @flatunsort;
# while (($stype,$yr) = each(%yearsum)) {
#        push(@flatunsort,[$stype,$yr,$yearsum{$stype}{$yr}]);
# }
# @flatsort = sort { $$b[0] cmp $$a[0] || $$b[1] <=> $$a[1] } @flatunsort;
# print join("\n", map { join(" ", @$_) } @flatsort), "\n";

# Example 2 - Multidimensional Hash sort
my @sorted_key1;
my %sorted_key2;

# create bins
$bstart[0]=1944;
$bend[0]=1945;
$nb=1;
# 1 year bins to 2020
while ($bend[$nb-1]<2020) {
	$bstart[$nb]=$bend[$nb-1];
	$bend[$nb]=$bstart[$nb]+1;
	$nb++;
}
# 2 years for to 2100
while ($bend[$nb-1]<2100) {
        $bstart[$nb]=$bend[$nb-1];
        $bend[$nb]=$bstart[$nb]+2;
        $nb++;
}

# 10 years for 500 years
while ($bend[$nb-1]<2670) {
        $bstart[$nb]=$bend[$nb-1];
        $bend[$nb]=$bstart[$nb]+10;
	$nb++;
}
# 100 years for rest
while ($bend[$nb-1]<12070) {
	$bstart[$nb]=$bend[$nb-1];
        $bend[$nb]=$bstart[$nb]+100;
	$nb++;
}
for ($i=0;$i<$nb;$i++) {
        for ($j=0;$j<$nsim2rad;$j++) {
                $bmass[$i][$j]=0.0;
        }
	$lvol[$i]=0.0;
}

foreach $key1 (sort keys %sitesum) {
	push @sorted_key1,$key1;
	@{ $sorted_key2{$key1} } = sort {$sitesum{$key1}{$b} <=> $sitesum{$key1}{$a}} keys %{$sitesum{$key1}};
}
$flag = 0;
$tot=0.0;
printf(OS "\nSolid and Liquid Waste Sites - Summary in Sorted Site Order (large to small)\n");
foreach $key1 (@sorted_key1){
	if ($flag == 0) {
		$lkey=$key1;
		$la="";
		$tot=0.0;
                $lb="";
		$flag=1;
	}
	if ($key1 ne $lkey) {
		$la=$lkey.",total".$la;
                $lb=$lkey.",".sprintf("%12.5e",$tot).$lb;
		print(OS "$la,\n");
		print(OS "$lb,\n\n");
		$la="";
                $lb="";
		$tot=0.0;
		$lkey=$key1;
	}
	foreach $key2 (@{ $sorted_key2{$key1} } ){
		$la=$la.",".$key2;
		$tot=$tot+$sitesum{$key1}{$key2}+0.0;
		$lb=$lb.",".sprintf("%12.5e",$sitesum{$key1}{$key2});
	}
}
$la=$lkey.",total".$la;
$lb=$lkey.",".sprintf("%12.5e",$tot).$lb;
print(OS "$la,\n");
print(OS "$lb,\n");
print(OS "\n\n");

printf(OS "\nLiquid Waste Sites - Summary in Constant Site Order (liquid volume large to small)\n");
undef @sorted_key1;
undef %sorted_key2;
$keyliquid="liquid";
foreach $key1 (sort keys %sitesuml) {
        push @sorted_key1,$key1;
        @{ $sorted_key2{$key1} } = sort {$sitesuml{$keyliquid}{$b} <=> $sitesuml{$keyliquid}{$a}} keys %{$sitesuml{$keyliquid}};
#	 @{ $sorted_key2{$key1} } = sort keys %swidh;

}
$flag = 0;
$tot=0.0;
foreach $key1 (@sorted_key1){
        if ($flag == 0) {
                $lkey=$key1;
                $la="";
                $tot=0.0;
                $lb="";
                $flag=1;
        }
        if ($key1 ne $lkey) {
                $la=$lkey.",total".$la;
                $lb=$lkey.",".sprintf("%12.5e",$tot).$lb;
                print(OS "$la,\n");
                print(OS "$lb,\n\n");
                $la="";
                $lb="";
                $tot=0.0;
                $lkey=$key1;
        }
        foreach $key2 (@{ $sorted_key2{$key1} } ){
                $la=$la.",".$key2;
		if (exists $sitesuml{$key1}{$key2}) {
                	$tot=$tot+$sitesuml{$key1}{$key2}+0.0;
                	$lb=$lb.",".sprintf("%12.5e",$sitesuml{$key1}{$key2});
		} else {
			$lb=$lb.",".sprintf("%12.5e",0.0);
		}
        }
}
$la=$lkey.",total".$la;
$lb=$lkey.",".sprintf("%12.5e",$tot).$lb;
print(OS "$la,\n");
print(OS "$lb,\n");
print(OS "\n\n");

#undef @sorted_key1;
#undef %sorted_key2;
#foreach $key1 (sort keys %yearsum) {
#        push @sorted_key1,$key1;
#        @{ $sorted_key2{$key1} } = sort {$yearsum{$key1}{$b} <=> $yearsum{$key1}{$a}} keys %{$yearsum{$key1}};
#}
#$flag = 0;
#$tot=0.0;
#foreach $key1 (@sorted_key1){
#        if ($flag == 0) {
#                $lkey=$key1;
#                $la="";
#                $lb="";
#                $flag=1;
#        }
#        if ($key1 ne $lkey) {
#		$la=$lkey.",total".$la;
#                $lb=$lkey.",".sprintf("%12.5e",$tot).$lb;
#                print(OS "$la,\n");
#                print(OS "$lb,\n\n");
#                $la="";
#                $lb="";
#                $tot=0.0;
#                $lkey=$key1;
#        }
#        foreach $key2 (@{ $sorted_key2{$key1} } ){
#		$la=$la.",".$key2;
#                $tot=$tot+$yearsum{$key1}{$key2}+0.0;
#                $lb=$lb.",".sprintf("%12.5e",$yearsum{$key1}{$key2});
#        }
#}
#$la=$lkey.",total,".$la;
#$lb=$lkey.",".sprintf("%12.5e",$tot).",".$lb;
#print(OS "$la,\n");
#print(OS "$lb,\n");
#print(OS "\n\n");

printf(OS "Liquid Waste Sites - Yearly totals\n");
undef @sorted_key1;
undef %sorted_key2;
foreach $key1 (sort keys %yearsum) {
        push @sorted_key1,$key1;
        @{ $sorted_key2{$key1} } = sort keys %yearh;
}
$flag = 0;
$tot=0.0;
foreach $key1 (@sorted_key1){
        if ($flag == 0) {
                $lkey=$key1;
                $la="";
                $lb="";
                $flag=1;
        }
        if ($key1 ne $lkey) {
                $la=$lkey.",total".$la;
                $lb=$lkey.",".sprintf("%12.5e",$tot).$lb;
                print(OS "$la,\n");
                print(OS "$lb,\n\n");
                $la="";
                $lb="";
                $tot=0.0;
                $lkey=$key1;
        }
	$kind=-1;
	for ($r=0;$r<$nsim2rad;$r++) {
        	if (lc($sim2radname[$r]) eq lc($key1)) {
			$kind=$r;
		}
	}
        foreach $key2 (@{ $sorted_key2{$key1} } ){
                $la=$la.",".sprintf("%6.1f",$key2);
		if (exists $yearsum{$key1}{$key2}) {
                	$tot=$tot+$yearsum{$key1}{$key2}+0.0;
			$lb=$lb.",".sprintf("%12.5e",$yearsum{$key1}{$key2});
			if (($kind != -1)) {
				# find bin year
				for ($b=0;$b<$nb;$b++) {
                                   if (($key2 >= $bstart[$b]) && ($key2 < $bend[$b])) {
					$bmass[$b][$kind]+=$yearsum{$key1}{$key2};
				   }
				}	
			}
			if (lc($key1) eq "liquid") {
				for ($b=0;$b<$nb;$b++) {
                                   if (($key2 >= $bstart[$b]) && ($key2 < $bend[$b])) {
                                        $lvol[$b]+=$yearsum{$key1}{$key2};
                                   }
                                }
			}
		} else {
			$lb=$lb.",".sprintf("%12.5e",0.0);
		}
        }
}
$la=$lkey.",total".$la;
$lb=$lkey.",".sprintf("%12.5e",$tot).$lb;

print(OS "$la,\n");
print(OS "$lb,\n");
print(OS "\n\n");

printf(OS "Solid Waste Sites\n");
for ($r=0;$r<$nsim2rad;$r++) {
	printf(OS "$sim2radname[$r]\n");
	$tot=0;
	printf(OS "SiteName, Start Year, End Year, Interval Activity ($sim2radunits), Yearly Rate ($sim2radunits/yr)\n");
	$lastname = "";
	$nameflag = 1;
	$sub=0;
	for ($k=0;$k<$nsws;$k++) {
		if (lc($sim2radname[$r]) eq lc($swsrad[$k])) {
			if (($nameflag == 0) && ($lastname ne $swssite[$k])) {
				printf(OS "Site total mass,,,%12.5e\n",$sub);
				$sub = 0;
			} 
			$nameflag = 0;
		printf(OS "$swssite[$k],%.1f,%.1f,%12.5e,%12.5e\n",$swssyear[$k],$swseyear[$k],$swsmean[$k],$swsyearlyrate[$k]);
			# find bin(s) to put this in
			$bn=0;
			for ($b=0;$b<$nb;$b++) {
				if (($swssyear[$k] >= $bstart[$b]) && ($swssyear[$k] < $bend[$b])) {
					if ($swseyear[$k] <= $bend[$b]) {
						$ny=$swseyear[$k]-$swssyear[$k];
					} else { 
						$ny=$bend[$b]-$swssyear[$k];
					}
					$bmass[$b][$r]+=$swsyearlyrate[$k]*$ny;
					# see if record in other bins too
					$bn=$b+1;
					while (($bn < $nb) && ($swseyear[$k] >= $bstart[$bn])){
                                        	if ($swseyear[$k] <= $bend[$bn]) {
                                                	$ny=$swseyear[$k]-$bstart[$bn];
                                        	} else {
                                                	$ny=$bend[$bn]-$bstart[$bn];
                                        	}
                                        	$bmass[$bn][$r]+=$swsyearlyrate[$k]*$ny;
						$bn++;
					}
				}
			}
			$lastname=$swssite[$k];
			$tot += $swsmean[$k];
			$sub += $swsmean[$k];
		}
	}
	printf(OS "Total Activity ($sim2radname[$r]),,,%12.5e\n\n",$tot);
}

printf(OT "Totals - liquid and solid sites (binned)\n");
printf(OT "Start Year, End Year,");
printf(OT "Liquid,");
for ($i=0;$i<$nsim2rad;$i++) {
	printf(OT "$sim2radname[$i],")
}
printf(OT "\n");
printf(OT ",,m^3,");
for ($i=0;$i<$nsim2rad;$i++) {
        printf(OT "$sim2radunits,")
}
printf(OT "\n");
for ($j=0;$j<$nsim2rad;$j++) {
	$atot[$j]=0;
}
$ltot=0;
for ($i=0;$i<$nb;$i++) {
	printf(OT "%.1f,%.1f,",$bstart[$i],$bend[$i]);
	printf(OT "%12.5e,",$lvol[$i]);
	$ltot+=$lvol[$i];
	for ($j=0;$j<$nsim2rad;$j++) {
		printf(OT "%12.5e,",$bmass[$i][$j]);
		$atot[$j]+=$bmass[$i][$j];
	}
	printf(OT "\n");
}
printf(OT "Totals,,");
printf(OT "%12.5e,",$ltot);
for ($j=0;$j<$nsim2rad;$j++) {
        printf(OT "%12.5e,",$atot[$j]);
}
printf(OT "\n");


close(SR);
close(SN);
close(OL);
close(OA);
close(OS);
close(OT);
