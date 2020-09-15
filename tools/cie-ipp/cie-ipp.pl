#!/usr/bsn/perl -w
# $RCSfile$ $Date$ $Author$ $Revision$
# cie-ipp.pl
# Created by MDWilliams, 1-5-2019`
# 	SIMV2 Appendix F Inventory Preprocessr
#		assumes the file has been sorted by CA Name, Date, and Waste Type
#	Removes Blank lines in Appendix F
#	Adds in Solid waste model releases
#	Adds in water only sites from SAC
#	Ditch / Trench / Pond flow routing
#	verifies sites in ehsit, SAC, and SIMV2 Appendix F
#
#   Args:
#	eshit file name
#	Appendix F SIMV2 (sorted) - RADS
#       Chemical Inventory (or none) - e.g. NO3, Cr, CN
#	SAC Liquid Inventory
#	(not active for cie) Solid waste Release Directory
#	(not active for cie) Solid waste Summary file (filenames)
#	Redistribution File name (or none)
#	New Inventory File Name (prefix) and log file
#	
#	v4.0 new solid waste files
#
#	v4.1 new solid waste files - slightly different summary file format
#
#	v4.2 - integrating solid waste release in summary file
#	
#	v4.3 - new solid waste file - reduced data cumulative solid waste
#
#	v4.4 = fixed bug in summary totals
#
#       v4.5 - Fixed a bug in additing additional solid waste sites (not in inventory(
#
#	v4.6 - fixed error calculating sacsum for summary file, also removed unused variable names
#
#	v4.7 - fixed bug where skipped liquid waste reporting for solid waste sites in summary file.
#
#	v4-8 - Copied cie-ipp.pl from ca-ipp.pl on 7-28.  New file layout for chem data for CIE, removing calculation for automatici generation of 
#	       U (g) since its now in the chem data file.  Removed routing file - now just one file name on command line.  Also removed solid waste 
#	       file release input (not needed for cie).  These were made to streamline and limit feature testing needs.
#
#	v4-9 - only writing out cie solutes
#
#	v4.10 - picthing solids and liquid/solids. writing to an excluded file.
#
#	v4.11 - combining multiple records for a year (typically a liquid and a entrained solid)
#
#	v4-12 - Bug fix.  It was skipping SAC water sources when there were only solid sources
#		in SIMV2.
#
#	v4-14 - modification to adding water from SAC, don't do it for Tanks (241-) and continue
#		skipping them for only solid sources in SIMV2.
#
#	v4-15 - had to add back SAC water sources for C Tanks, fixed rounding errors when summing
#		multiple records (was rounding every time - now only rounding at the end when writing.
#	v4-16 - fixed rounding errors when summing multiple records (was rounding every time - now only
#		rounding at the end when writing.

	
$dtstamp = localtime();

$vers="9/14/2020 Ver 4.16 by MDWilliams, Intera Inc.";

#
$ehsit = shift @ARGV;
$radinv = shift @ARGV;
$cheminv = shift @ARGV;
$liqinv = shift @ARGV;
#$swrdir = shift @ARGV;
#$swrind = shift @ARGV;
$swrdir = "none";
$swrind = "none";
$redfn = shift @ARGV;
$outpref = shift @ARGV;
$outpref =~ s/[\r\n]+$//;
chomp($outpref);

$outlog=$outpref.".log";
$outinv=$outpref.".csv";
$outsum=$outpref."-summary.csv";
$outex=$outpref."-exclude.csv";

open(SG,"<$ehsit") || die "Can't open $ehsit file $!\n";
open(SR,"<$radinv") || die "Can't open $radinv file $!\n";
if ($cheminv ne "none" ) {
	open(SC,"<$cheminv") || die "Can't open $cheminv file $!\n";
}
open(SL,"<$liqinv") || die "Can't open $liqinv file $!\n";
if ($swrdir ne "none") {
	open(SWI,"<$swrind") || die "Can't open $swrind file $!\n";
}
if ($redfn ne "none") {
	open(RF,"<$redfn") || die "Can't open $redfn file $!\n";
}
open(OL,">$outlog") || die "Can't open $outlog file $!\n";
open(OI,">$outinv") || die "Can't open $outinv file $!\n";
open(OS,">$outsum") || die "Can't open $outsum file $!\n";
open(OX,">$outex") ||  die "Can't open $outex file $!\n";

@cies=("H-3","I-129","Sr-90","Tc-99","U","Cr","NO3","CN");
@cie_hash={};
for ($i=0;$i<scalar(@cies);$i++) {
	$cie_hash{$cies[$i]} = -1;
}

$dashes="----------------------------------------------------------------------";
printf(OL "Inventory preprocessor ca-ipp.pl Log File: $dtstamp\n");
printf(OL "# Processed by CIE-IPP $vers\n");
printf(OL "# ehsit file = $ehsit, Rad Inventory file = $radinv\n");
printf(OL "# Chemical Inventory file = $cheminv\n");
printf(OL "# Rerouting file = $redfn.  Note: only includes CIE Solutes\n");
printf(OL "# SAC supplemental Liquids = $liqinv\n");
printf(OL "# Solid Waste Inventory Directory = $swrdir\n");
printf(OL "$dashes\n$dashes\n");

printf(OI "CIE Inventory: $dtstamp\n");
printf(OI "# Processed by CIE-IPP $vers\n");
printf(OI "# ehsit file = $ehsit, Rad Inventory file = $radinv\n");
printf(OI "# Chemical Inventory file = $cheminv\n");
printf(OI "# Rerouting file = $redfn.  Note: only includes CIE Solutes\n");
printf(OI "# SAC supplemental Liquids = $liqinv\n");
#printf(OI "# Solid Waste Inventory Directory = $swrdir\n\n");
printf(OI "\n");

printf(OS "# Inventory Summary for $outinv: $dtstamp\n");
printf(OS "# Processed by CIE-IPP $vers\n");
printf(OS "# ehsit file = $ehsit, Rad Inventory file = $radinv\n");
printf(OS "# Chemical Inventory file = $cheminv, SAC supplemental Liquids = $liqinv\n");
printf(OS "# Solid Waste Inventory Directory = $swrdir\n\n");
printf(OS "# Rerouting file = $redfn.  Note: only includes CIE Solutes\n");

printf(OX "CIE Inventory - excluded: $dtstamp\n");
printf(OX "# Processed by CIE-IPP $vers\n");
printf(OX "# ehsit file = $ehsit, Rad Inventory file = $radinv\n");
printf(OX "# Chemical Inventory file = $cheminv\n");
printf(OX "# Rerouting file = $redfn.  Note: only includes CIE Solutes\n");
printf(OX "# SAC supplemental Liquids = $liqinv\n");
#printf(OI "# Solid Waste Inventory Directory = $swrdir\n\n");
printf(OX "\n");

printf(OL "\n$dashes\n$dashes\n");
printf(OL "Loading $ehsit\n");
# load ehsit (shapefile of waste sites, converted to csv)
# skip header
$line = <SG>;
$nhsit=0;
while ($line = <SG>) {
    chomp($line);
    $line =~ s/\r//g;
    @a =split(",",$line);
    if ($a[0] ne '')  {
    	$ehsitname[$nhsit]=uc($a[0]);
	$nhsit++;
    } 
    # don't need geometries for this code
}
close(SG);

@ehsit_hash = {};
# Make Hash of ehsit wastesite names
$nd=0;
printf(OL "List of Duplicate sites in $ehsit:\n");
for ($i=0;$i<$nhsit;$i++) {
		if (exists $ehsit_hash{$ehsitname[$i]}) {
			printf(OL "Duplicate site = $ehsitname[$i]\n");
			$nd++;
		} else {
			$ehsit_hash{$ehsitname[$i]} = $i;
		}
}
if ($nd == 0) {
	printf(OL "none\n");
}
$nhkeys = scalar keys %ehsit_hash;
if ($nhkeys != ($nhsit-$nd)) {
	printf(OL "sfu#1 $nhkeys, $nhsit, $nd\n");
}
printf(OL "# of unique wastesites in ehsit ($ehsit) = $nhkeys\n");
printf(OL "$dashes\n$dashes\n");

printf(OL "\n$dashes\n$dashes\n");
printf(OL "Loading $radinv\n");
# load SIM Inventory
# skip first line
$line = <SR>;
chomp($line);
$line =~ s/\r//g;
printf(OI "# Inventory File Header = $line\n\n");
printf(OS "# Inventory File Header = $line\n\n");
printf(OL "# Inventory File Header = $line\n\n");
printf(OX "# Inventory File Header = $line\n\n");
$line = <SR>;
chomp($line);
$line =~ s/\R//g;
printf(OI "# Inventory File Header = $line\n\n");
printf(OS "# Inventory File Header = $line\n\n");
printf(OL "# Inventory File Header = $line\n\n");
printf(OX "# Inventory File Header = $line\n\n");

# load header - 2 lines (units and rads)
$line = <SR>;
chomp($line);
$line =~ s/\r//g;

@a=split(",",$line);
$sim2radunits=$a[6];
if (lc($sim2radunits) =~ m/curies/) {
      $sim2radunits = "Ci";
} else {
	printf("Error - unknown units in 3rd line, Column 7 = $sim2radunits\n");
	exit(0);
}
	
$line = <SR>;
chomp($line);
$line =~ s/\r//g;
# printf(OI "$line\n");
@hu=split(",",$line);

#find year, volume, site, source, and units columns
$nhu=scalar(@hu);
$sim2volunits="";
for ($i=0;$i<$nhu;$i++) {
	if (lc($hu[$i]) =~ m/ca site name/) {
		$casitecol = $i;
	} elsif (lc($hu[$i]) =~ m/simv2 site name/) {
#		$sim2sitecol = $i;
	} elsif (lc($hu[$i]) =~ m/source/) {
		$sim2sourcecol = $i;
	} elsif (lc($hu[$i]) =~ m/volume/) {
		$sim2volcol=$i;
		($sim2volunits) = $hu[$i] =~ /\[(.*)\]/;
		if ($sim2volunits eq "m3") {
			$sim2volunits = "m^3";
		} else {
			printf("Error - unkown Volume units = $sim2volunits\n");
			exit(0);
		}
	} elsif (lc($hu[$i]) =~ m/discharge/) {
		$sim2timecol = $i;
		@a = split(" ", $hu[$i]);
		$sim2timeunit = $a[1];
#	} elsif (lc($hu[$i]) =~ m/curies/) {
#		$sim2radunits = "Ci";
	} elsif (lc($hu[$i]) =~ m/inventory module/) {
		$sim2modulecol = $i;
	}

}

@hr=split(",",$line);
$nhr=scalar(@hr);
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
 	    $sim2radname[$nsim2rad]=$s2r;
 	    $nsim2rad++;
	}
}
printf("NSIM2RAD = $nsim2rad\n");
$nchem=0;
$chemsitecol=-1;
$chemtypecol=-1;
$chemyearcol=-1;
$chemvolcol=-1;
# Add in chems to header
if ($cheminv ne "none") {
	# read single header line
	$line = <SC>;
	chomp($line);
	$line =~ s/\r//g;
	@chemh=split(",",$line);
	$nchemh=scalar(@chemh);
	for ($i=0;$i<$nchemh;$i++) {
		if ($chemh[$i] =~ m/CIE Site Name/i) {
			$chemsitecol=$i;
		} elsif ($chemh[$i] =~ m/Source Type/i) {
			$chemtypecol=$i;
		} elsif ($chemh[$i] =~ m/Year/i) {
			$chemyearcol = $i;
		} elsif ($chemh[$i] =~ m/Volume Mean/i) {
			$chemvolcol = $i;
			$chemh[$i] =~ s/\[/ /g;
			$chemh[$i] =~ s/\]//g;
			@a=split('  ',$chemh[$i]);
#			$chemvolunits=$a[1];
		}
	}
	$chemstartcol=$chemvolcol+1;
	$nchem = $nchemh - $chemstartcol;
	printf("nchem=$nchem, startcol=$chemstartcol\n");
	@chemname=[];
	@chemunits=[];
	@chempos=[];
	for ($i=0;$i<$nchem;$i++) {
		$cnu = $chemh[$i+$chemstartcol];
		$cnu =~ s/\[/ /g;
		$cnu =~ s/\]//g;
		@a = split('  ',$cnu);
		# reorder for inventory file
		if ($a[0] =~ m/U-Total/i) {
			$a[0]="U";
			$chempos[$i]=0;
		} elsif ($a[0] =~ m/Cr/i) {
			$chempos[$i]=1;
		} elsif ($a[0] =~ m/NO3/i) {
			$chempos[$i]=2;
		} elsif ($a[0] =~ m/CN/i) {
			$chempos[$i]=3;
		} else {
			printf("Error - Unrecognized Chem = $a[0]\n");
			printf("Program stopped\n");
			exit(0);
		}
		$chemname[$chempos[$i]]=$a[0];
		$chemunits[$chempos[$i]]=$a[1];
		printf("chem name=$chemname[$chempos[$i]], units=$chemunits[$chempos[$i]], position=$chempos[$i]\n");
	}
}
#$totcols=$nhr+$nchem;
#$mergechemcol=$nhr;

printf(OI "$hu[0],$hu[1],$hu[2],$hu[3],$hu[4],$hu[5],");
printf(OS "$hu[0],$hu[1],$hu[2],$hu[3],$hu[4],$hu[5],");
printf(OX "$hu[0],$hu[1],$hu[2],$hu[3],$hu[4],$hu[5],");
$ciecols=0;
@sim2cie=[];
for ($i=0;$i<$nsim2rad;$i++) {
	if (exists($cie_hash{$sim2radname[$i]})) {
		$cie_hash{$sim2radname[$i]}=$ciecols;
		$sim2cie[$i]=$ciecols;
		$ciecols++;
		printf(OI "$sim2radname[$i],");
		printf(OS "$sim2radname[$i],");
		printf(OX "$sim2radname[$i],");
	} else {
		printf("Excluded = $sim2radname[$i]\n");
		$sim2cie[$i]=-1;	
	}
}
$cieradcols=$ciecols;
$mergechemcol=$cieradcols+6;
printf("Mergechemcol = $mergechemcol\n");
@chem2cie=[];
for ($i=0;$i<$nchem;$i++) {
	$cie_hash{$chemname[$i]}=$ciecols;
	$chem2cie[$i]=$mergechemcol+$chempos[$i];
	$ciecols++;
	printf(OI  "$chemname[$i],");
	printf(OX  "$chemname[$i],");
	printf(OS  "$chemname[$i],");
}
$ciechemcols=$ciecols-$cieradcols;
printf(OI "\n");
printf(OX "\n");
printf(OS "\n");
printf(OI ",,,,$sim2volunits,$sim2timeunit,");
printf(OX ",,,,$sim2volunits,$sim2timeunit,");
printf(OS ",,,,$sim2volunits,$sim2timeunit,");
for ($i=0;$i<$cieradcols;$i++) {
        printf(OI "$sim2radunits,");
	printf(OS "$sim2radunits,");
	printf(OX "$sim2radunits,");
}
for ($i=0;$i<$ciechemcols;$i++) {
        printf(OI "$chemunits[$i],");
	printf(OS "$chemunits[$i],");
	printf(OX "$chemunits[$i],");
}
printf(OI "\n");
printf(OS "\n");
printf(OX "\n");
my %yearh;
my %swidh;
@simv2_hash = {};
@simv2_count = {};
$il=0;
$nsimsites=0;
while ($line=<SR>) {
	# load sim inventory
	chomp($line);
	$line =~ s/\r//g;
#	$slines[$il]=$line;
	@yl=split(",",$line);
	$swid=uc($yl[$casitecol]);
	$swid =~ tr/\"//d;
	$swid =~ s/^\s+|\s+$//g;
	$date=$yl[$sim2timecol];
	if (!defined $date) {
		$date="";
	}
	if ($date eq "") {
		printf(OL "Zero date in SIMV2 - Line tossed: $line\n");
	} else {
#	$yltype= lc($yl[$sim2sourcecol]);
#	$yltype =~ s/^\s+|\s+$//g;
#	$ylmodule = lc($yl[$sim2modulecol]);
#	$ylmodule =~ s/^\s+|\s+$//g;
	    $dupln=-1; 
	    if (exists $simv2_hash{$swid}) {
		# check if date already exists (dup years)
		$nl=$simv2_count{$swid};
		$sl=$simv2_hash{$swid};
		for ($i=0;$i<$nl;$i++) {
			$dline=$slines[$sl+$i];
			@dup=split(",",$dline);	
			if ($date eq $dup[$sim2timecol]) {
				$dupln=$i;
				last;
			} 
		}
		if ($dupln == -1) {
			$simv2_count{$swid}++;
		}
            } else {
		$simv2_site[$nsimsites]=$swid;
		$nsimsites++;
                $simv2_hash{$swid} = $il;
		$simv2_count{$swid} = 1;
            }

	    # get only CIE Solutes
	    if ($dupln == -1) {
	      $line="";
	      for ($i=0;$i<6;$i++) {
		$line=$line.$yl[$i].",";
	      }
	      for ($i=0;$i<$ntrad;$i++) {
		if ($sim2cie[$i] != -1) {
			if (exists $yl[6+$i]) {
				$line=$line.$yl[6+$i].",";
			} else {
				$line=$line.",";
			}
		}
	     }
	     # append blanks for chems (not in SIMv2)
	     for ($i=0;$i<$ciechemcols;$i++) {
		$line=$line.",";
	     }
	     $slines[$il]=$line;
	     $il++;
	    } else {
		printf("dup site/date\n");
		printf("$dline\n");
		for ($t=0;$t<6;$t++) {
			printf("$yl[$t],");
		}
		for ($t=0;$t<$ntrad;$t++) {
			if ($sim2cie[$t] != -1) {
			    if (exists $yl[6+$t]) {
				printf("$yl[6+$t],");
			    } else {
				printf(",");
			    }
			}
		}
		printf("\n");
		# replace existing line for this date
		$line = $dup[0]." and ".$yl[0].",".$yl[1].",".$yl[2].",";
		# determine source type and volume
		if ($dup[$sim2sourcecol] eq $yl[$sim2sourcecol]) {
			# both either liquid or solid
			$v="";
			$r1=0.0;
			$r2=0.0;
			if ((exists $dup[$sim2volcol]) && ($dup[$sim2volcol] ne "")) {
				$r1=$dup[$sim2volcol];
			}
			if ((exists $yl[$sim2volcol]) && ($yl[$sim2volcol] ne "")) {
				$r2=$yl[$sim2volcol];
			}
			if (($r1 > 0.0) || ($r2 > 0.0)) {
				$v=$r1+$r2;
#				$r1=$r1+$r2;
#				$v = sprintf("%.7e",$r1);
			}
			$line=$line.$yl[$sim2sourcecol].",".$v.",";
		} else {
			if ($dup[$sim2sourcecol] =~ /liquid/i) {
				$line=$line.$dup[$sim2sourcecol].",".$dup[$sim2volcol].",";
			} elsif ($yl[$sim2sourcecol] =~ /liquid/i) {
				$line=$line.$yl[$sim2sourcecol].",".$yl[$sim2volcol].",";
			} else {
				printf("Don't know what we've got on dup merge = @yl and @dup\n");
				exit(0);
			}
		}

		# year
		$line=$line.$yl[$sim2timecol].",";

		# add rads together
		$addcol=0;
                for ($i=0;$i<$ntrad;$i++) {
                  if ($sim2cie[$i] != -1) {
			$tot="";
			$r1=0.0;
			$r2=0.0;
                        if ((exists $yl[6+$i]) && ($yl[6+$i] ne "")) {
                                $r1=$yl[6+$i];
                        }
			if ((exists $dup[6+$addcol]) && ($dup[6+$addcol] ne "")) {
				$r2=$dup[6+$addcol];
                        }
			if (($r1 > 0.0) || ($r2 > 0.0)) {
				$tot=$r1+$r2;
#				$tot=sprintf("%.7e",$tot);
			}
			$line=$line.$tot.",";
			$addcol++;
                  }
               }
               # append blanks for chems (not in SIMv2)
               for ($i=0;$i<$ciechemcols;$i++) {
                  $line=$line.",";
               }
	       printf("Combo=\n$line\n");
	       $slines[$sl+$dupln]=$line;
	   }
	}
}
close(SR);
# load CHEM Inventory (if exists);
if ($cheminv ne "none") {
        printf(OL "\n$dashes\n$dashes\n");
        printf(OL "Loading $cheminv - merging with Rad Inventory\n");
	while ($line = <SC>) {
	  chomp($line);
	  $line =~ s/\r//g;
	  printf("chem merge\n");
	  printf("$line\n");
 	  @a=split(",",$line);
	  $cswid=uc($a[$chemsitecol]);
          $cswid =~ tr/\"//d;
          $cswid =~ s/^\s+|\s+$//g;
	  $cyear=$a[$chemyearcol];
	  # swap chem cols to match cie inventory
	  @ta=@a;
	  for ($i=0;$i<$nchem;$i++) {
		$a[6+$chempos[$i]]="";
		if ((exists $ta[6+$i]) && ($ta[6+$i] ne "")) {
			$a[6+$chempos[$i]]=$ta[6+$i];
		}
	  }
	  if ($cyear > 0.0) {
	    # find match in Rad Inventory
	    if (exists $simv2_hash{$cswid}) {
		$sl = $simv2_hash{$cswid};
		$nl = $simv2_count{$cswid};
		$mflag = -1;
		for ($i=0;$i<$nl;$i++) {
		    @s = split(",",$slines[$sl+$i]);
		    if ($s[$sim2timecol] == $cyear) {
			 printf("$slines[$sl+$i]\n");
			# check for waste type
		        if ((($a[$chemtypecol] =~ m/solid/i) && ($s[$sim2sourcecol] =~ m/solid/i)) || 
		         (($a[$chemtypecol] =~ m/liquid/i) && ($s[$sim2sourcecol] =~ m/liquid/i))) {
				# waste types match
			} else {
			  if (($s[$chemtypecol] =~ m/solid/i) && ($s[$sim2modulecol] =~ /entrained/i)) {
				# ok - will be changed to liquid later
			  } else {
printf("Warning: Chem merge Mismatched waste types for $cswid,$cyear,simv2=$s[$sim2sourcecol],chem=$a[$chemtypecol]");
printf(" - Merged anyway\n");
printf(OL "Warning: Chem merge Mismatched waste types for $cswid,$cyear,simv2=$s[$sim2sourcecol],chem=$a[$chemtypecol]");
printf(OL " - Merged anyway\n");
            		  }
			}
			# check volumes
			if (exists($a[$chemvolcol]) && ($a[$chemvolcol] ne "")) {
			  if ($a[$chemvolcol] ne $s[$sim2volcol]) {
			    if (($a[$chemtypecol] !~ m/solid/i) && ($s[$sim2sourcecol] !~ m/solid/i)) {
printf("Warning - SIMV2 and Chem data have different volumes: $cswid,$cyear,simv2=$s[$sim2volcol],chem=$a[$chemvolcol]");
printf(" - chem volume ignored\n");
printf(OL "Warning - SIMV2 and Chem data have different volumes: $cswid,$cyear,simv2=$s[$sim2volcol],chem=$a[$chemvolcol]");
printf(OL " - chem volume ignored\n");
			    }
			  }
			}

			$mflag=$sl+$i;
			# update with chems
			for ($j=0;$j<$nchem;$j++) {
			    if (exists($a[6+$j]) && ($a[6+$j] ne "")) {
				if ($a[6+$j] > 0.0) {
				    if ((exists($s[$mergechemcol+$j])) && ($s[$mergechemcol+$j] > 0.0)) {
					$s[$mergechemcol+$j]=$s[$mergechemcol+$j] + $a[6+$j];
#					$v = $s[$mergechemcol+$j];
#					$s[$mergechemcol+$j]=sprintf("%.7e",$v);
				    } else {
					 $s[$mergechemcol+$j]=$a[6+$j];
				    }
				}
			    }
                        }
			# build line again
			$tline=$s[0]." and ".$a[0]."(chem),";
			for ($j=1;$j<$ciecols+6;$j++) {
				if ((exists($s[$j])) && ($s[$j] ne "")) {
					$tline=$tline.$s[$j].",";
				} else {
					$tline=$tline.",";
				}
			}
			printf("$tline\n");
			$slines[$sl+$i]=$tline;
			last;
		    }
		}
		if ($mflag == -1) {
			printf("Error - Can't find chem site/year in simv2: $cswid, $cyear\n");
			printf("Stopping\n");
                        printf(OL "Error - Can't find chem site/year in simv2: $cswid, $cyear\n");
                        printf(OL "Stopping\n");
			exit(0);

		}
	    } else {
		printf("Warning: $cswid (chem) not in simv2 - added single record (special case for C Tanks)\n");
		printf(OL "Warning: $cswid (chem) not in simv2 - added single record (special case for C Tanks)\n");
                $simv2_site[$nsimsites]=$cswid;
                $nsimsites++;
                $simv2_hash{$cswid} = $il;
                $simv2_count{$cswid} = 1;
		# fill in 
		$tline=$a[0].",".$a[1].",".$a[2].",".$a[3].",".$a[5].",".$a[4].",";
		for ($i=0;$i<$cieradcols;$i++) {
			$tline=$tline.",";
		}
		for ($i=0;$i<$nchem;$i++) {
			$tline=$tline.$a[6+$i].",";

		}
		$slines[$il]=$tline;
		$il++
	    }
	  }
	}
	close(SC);
}

$nsimkeys = scalar keys %simv2_hash;
printf(OL "\n# of unique wastesites in $radinv = $nsimkeys ($nsimsites)\n");
printf(OL "$dashes\n$dashes\n");

printf(OL "\n$dashes\n$dashes\n");
printf(OL "Loading $liqinv\n");
$nsac=0;
$sd=0;
$sac_hash = {};
# skip header
$line=<SL>;
printf(OL "\nDuplicate waste sites in $liqinv:\n");
while ($line=<SL>) {
    # load SAC Water sources
    chomp($line);
    $line =~ s/\r//g;
    @sl=split(",",$line);
    $swid=uc($sl[0]);
    $swid =~ tr/\"//d;
    $swid =~ s/^\s+|\s+$//g;
    $sacname[$nsac]=$swid;
    $nyear=$sl[1];
    if ($nyear != 0) {
        if (exists $sac_hash{$swid}) {
		printf(OL "Duplicate waste site = $swid\n");
		$sd++;
        } else {
                $sac_hash{$swid} = $nsac;
        }
        $nyear=$sl[1];
	$sacnyears[$nsac]=$nyear;
        # load up years of data
        for ($i=0;$i<$nyear;$i++) {
                $ylval[$i]=0;
                $line=<SL>;
                chomp($line);
		$line =~ s/\r//g;
                @yl=split(",",$line);
		$sacyear[$nsac][$i]=$yl[0];
                $radlines=$yl[2];
		$ylunit=$yl[3];
                $ylunit =~ tr/\"//d;
		$saclunit[$nsac][$i]=$ylunit;
                $yltype=$yl[4];
                $yltype=~ tr/\"//d;
                if ((defined $yl[5]) && ($yl[5] ne '')) {
                        $ylval[$i]=$yl[5];
			$sacliq[$nsac][$i]=$yl[5];
                } else {
			$sacliq[$nsac][$i]=0;
		}
                # load up rads for the year
                for ($j=0;$j<$radlines;$j++) {
                    $line=<SL>;
                    chomp($line);
		    $line =~ s/\r//g;
                    @r=split(",",$line);
                    $r[0]=~ tr/"//d;
		    # note: Not using SAC rads
#                    if ($r[2] != 0.0) {
#                        if (exists $radind{$r[0]}) {
#                                $t=$radind{$r[0]};
#                                $radsum[$t]+=$r[2];
#                                $yrad[$nyrad[$t]][$t]=$r[2];
#                                $yrrad[$nyrad[$t]][$t]=$year[$i];
#                                $nyrad[$t]++;
#                        } else {
#                                $r[1]=~ tr/"//d;
#				$radname[$nrad]=$r[0];
#                                $radunits[$nrad]=$r[1];
#                                $radsum[$nrad]=$r[2];
#                                $yrad[0][$nrad]=$r[2];
#                                $yrrad[0][$nrad]=$year[$i];
#                                $nyrad[$nrad]=1;
#                                $radind{$r[0]}=$nrad;
#                                $nrad++;
#                        }
#                     }
            	} 
   	}
	$nsac++;
    }
}
close(SL);
if ($sd == 0) {
	printf(OL "none\n");
}
$nsackeys = scalar keys %sac_hash;
if ($nsackeys != ($nsac-$sd)) {
        printf(OL "sfu#1 $nsackeys, $nsac, $sd\n");
}
printf(OL "# of unique wastesites in SAC Liquid Inventory ($liqinv) = $nsackeys\n");
printf(OL "$dashes\n$dashes\n");

printf(OL "\n$dashes\n$dashes\n");
printf(OL "Processing WasteSite Rerouting ...\n");
printf(OL "$dashes\n$dashes\n");
# reroute sources
if ($redfn ne "none") {
    printf(OL "Replacing / supplementing Sources based on $redfn\n");
    # two header lines
    for ($i=0;$i<2;$i++) {
               $line = <RF>;
    }
    $lastsite="";
    while ($line = <RF>) {
        chomp($line);
	$line =~ s/\r//g;
        @a=split(",",$line);
        $rsit=$a[$casitecol];
        if ($lastsite ne $rsit) {
            # delete out old site or add new one
	    if (exists $simv2_hash{$rsit}) {
                printf(OL "Deleting old records for $rsit, nrecs=$simv2_count{$rsit}\n");
                # point to end of the list
		$ol=$simv2_hash{$rsit};
		for ($i=0;$i<$simv2_count{$rsit};$i++) {
			$slines[$ol+$i]="";
		}
	    } else {
		printf(OL "Adding a new site to Inventory $rsit\n");
		$simv2_site[$nsimsites]=$rsit;
		$nsimsites++;
	    }
    	    $simv2_hash{$rsit}=$il;
            $simv2_count{$rsit}=0;
	}
        printf(OL "Reroute: $line\n");
        $slines[$il]=$line;
        $il++;
        $simv2_count{$rsit}++;
        $lastsite = $rsit;
    }
}
printf(OL "\n$dashes\n$dashes\n");

# load Solid Waste Sites
# read index - skip header
$nsws=0;
$nswsites=0;
if ($swrdir ne "none") {
  printf(OL "Loading Solid Waste Release Site Index $swrind\n");
  # skip header
  $line = <SWI>;
  $nsws=0;
  $nswsites=0;
  @sws_hash = {};
  while ($line = <SWI>) {
        chomp($line);
	$line =~ s/\r//g;
        @a=split(",",$line);
        $swname[$nsws]=$a[1];
	$swcopc[$nsws]=$a[0];
	$swredactivity[$nsws]=$a[6];
#	$swfile[$nsws]=$a[1]."_".$a[0].".csv";
	$swused[$nsws]=0;
        if (!exists $sws_hash{$swname[$nsws]}) {
	        $nswsites++;
                $sws_hash{$swname[$nsws]} = $nswsites;
	}
	$nsws++;
  }
  close(SWI);
}
printf(OL "Number of Solid Waste Release Sites = $nswsites\n");
printf(OL "$dashes\n$dashes\n\n");

printf(OL "$dashes\n$dashes\n");
printf(OL "Cross Checking Names between files\n");
printf(OL "$dashes\n$dashes\n");

# compare SIMV2 with ehsit
$m1=0;
$u1=0;
printf(OL "\nComparing wastesites in SIMV2 ($radinv) with ehsit($ehsit):\n");
for $sit (keys %simv2_hash) {
	if (exists $ehsit_hash{$sit}) {
		$m1++;
	} else {
		printf(OL "$sit not in ehsit\n");
		$u1++;
	}
}
printf(OL "number of matches = $m1, number of no matches = $u1\n");
printf(OL "$dashes\n$dashes\n");

# compare ehsit with SIMV2
$m2=0;
$u2=0;
printf(OL "\nComparing wastesites in ehsit ($ehsit) with SIMV2 ($radinv):\n");
for $sit (keys %ehsit_hash) {
        if (exists $simv2_hash{$sit}) {
                $m2++;
        } else {
                printf(OL "$sit not in SIMV2\n");
		$u2++;
        }
}
printf(OL "number of matches = $m2, number of no matches = $u2\n");
printf(OL "$dashes\n$dashes\n");

# compare SAC with ehsit
$m3=0;
$u3=0;
printf(OL "\nComparing wastesites in SAC Liquid Inventory ($liqinv) with ehsit ($ehsit):\n");
for $sit (keys %sac_hash) {
        if (exists $ehsit_hash{$sit}) {
                $m3++;
        } else {
                printf(OL "$sit not in ehsit\n");
		$u3++;
        }
}
printf(OL "number of matches = $m3, number of no matches = $u3\n");
printf(OL "$dashes\n$dashes\n");

# compare SAC with SIM
$m4=0;
$u4=0;
printf(OL "\nComparing wastesites in SAC Liquid Inventory ($liqinv) with SIMV2 ($radinv):\n");
for $sit (keys %sac_hash) {
        if (exists $simv2_hash{$sit}) {
                $m4++;
        } else {
                printf(OL "$sit not in SIMV2\n");
                $u4++;
        }
}

printf(OL "number of matches = $m4, number of no matches = $u4\n");
printf(OL "$dashes\n$dashes\n");


# compare solid waste release site with ehsit
$m5=0;
$u5=0;
printf(OL "\nComparing Solid Waste Release Sites with ehsit ($ehsit):\n");
for $sit (keys %sws_hash) {
        if (exists $ehsit_hash{$sit}) {
                $m5++;
        } else {
                printf(OL "$sit not in ehsit\n");
                $u5++;
        }
}
printf(OL "number of matches = $m5, number of no matches = $u5\n");
printf(OL "$dashes\n$dashes\n");


# compare solid waste release sites with Rad Inventory
$m6=0;
$u6=0;
printf(OL "\nComparing Solid Waste Release Sites with SIMV2 ($radinv):\n");
for $sit (keys %sws_hash) {
        if (exists $simv2_hash{$sit}) {
                $m6++;
        } else {
                printf(OL "$sit not in SIMV2\n");
                $u6++;
        }
}
printf(OL "number of matches = $m6, number of no matches = $u6\n");
printf(OL "$dashes\n$dashes\n");

printf(OL "\n\n$dashes\n$dashes\n");
printf(OL "Processing Inventory...\n");
printf(OL "$dashes\n$dashes\n");

# loop over Rad Inventory - waste site by waste site
for ($s=0;$s<$nsimsites;$s++) {
    $swid = $simv2_site[$s];
    $nl = $simv2_count{$swid};
    $ls = $simv2_hash{$swid};
    $flag=0;

    # solid waste release site?
    if (exists $sws_hash{$swid}) {
	$swsflag = 1;
    } else {
	$swsflag = 0;
    }
    $liqflag=0;
    for ($l=0;$l<$nl;$l++) {
	$line=$slines[$ls+$l];
	@sla=split(",",$line);
        $yltype= lc($sla[$sim2sourcecol]);
        $yltype =~ s/^\s+|\s+$//g;
        $ylmodule = lc($sla[$sim2modulecol]);
        $ylmodule =~ s/^\s+|\s+$//g;

	if ($ylmodule =~ m/entrained/i) {
		printf(OL "SimV2 Entrained Solids turned to Liquid Type: $line\n");
		$yltype = "Liquid";
		$line =~ s/,Solids/,Liquid/;
	}
	
#printf("Should it be skipped? $swsflag, $yltype");
#	if (($swsflag == 1) && (lc($yltype) =~ /olid/)) {
# CIE - SKIP All Solids
	if (lc($yltype) =~ /olid/) {

	    # pitch line if a solid, will replace with release
#	    printf("  Yes!\n");
#	    printf(OL "Solid Inventory Skipped, Replaced by Release: $line\n");
	    printf(OL "Solid Inventory Skipped for CIE: $line\n");
	    printf(OX "$line\n");
	} else {
	    $liqflag=1;
            # write out line
	    $rline=$line;
	    @r=split(",",$rline);
	    $line=$r[0].",".$r[1].",".$r[2].",".$r[3].",";
	    $t = sprintf("%.5e,",$r[4]);
	    $t =~ s/e/E/;
	    $line=$line.$t.$r[5].",";
	    # round rest of data to 6 sigfigs		
	    for ($i=0;$i<scalar(@r)-5;$i++) {
                        if ((!defined $r[6+$i]) || ($r[6+$i] eq "")) {
                            $line=$line.",";
                        } else {
		            $t=sprintf("%.5e",$r[6+$i]);
			    $t =~ s/e/E/;
			    $line=$line.$t.",";
			}
            }
            printf(OI "$line\n");

            # add to totals
	    if ($flag == 0) {
		$flag = 1;
		@tot = split(",",$line);
		$tot[0]="Total";
		$tot[$sim2sourcecol]="";
		if ((!defined $tot[$sim2volcol]) || ($tot[$sim2volcol] eq "")) {
			$tot[$sim2volcol]=0;
		}
		$tottmin=$tot[$sim2timecol];
		$tottmax=$tottmin;
		for ($i=0;$i<$ntrad+$nchem;$i++) {
			if ((!defined $tot[6+$i]) || ($tot[6+$i] eq "")) {
			    $tot[6+$i] = 0;
			}
		}
	    } else {
		@d=split(",",$line);
		if ($d[$sim2timecol] < $tottmin) {
			$tottmin=$d[$sim2timecol];
		}
		if ($d[$sim2timecol] > $tottmax) {
                        $tottmax=$d[$sim2timecol];
                }
		if ((defined $d[$sim2volcol]) && ($d[$sim2volcol] ne "")) {
		    $tot[$sim2volcol]+=$d[$sim2volcol];
		}

		for ($i=0;$i<$ntrad+$nchem;$i++) {
		    if ((defined $d[6+$i]) && ($d[6+$i] ne "")) {
		       $tot[6+$i]+=$d[6+$i];
		    }
		}

	    }
        }

    }

    # print total
    if (($swsflag == 0) || (($swsflag == 1) && ($liqflag != 0))) {
       for ($i=0;$i<5;$i++) {
        printf(OS "$tot[$i],");
       }
       printf(OS "%6.1F to %6.1F,",$tottmin, $tottmax);
       for ($i=0;$i<$ntrad+$nchem;$i++) {
        if (defined $tot[6+$i]) {
            printf(OS "%.5e,",$tot[6+$i]);
        } else {
            printf(OS ",");
        }
       }
       printf(OS "\n");
    }

    # insert solid waste release
    if (($swsflag == 1) || ($s == ($nsimsites-1))) {
     # if out of simv2 recs, add in any additional ones
     if (($swsflag == 1) && ($s < ($nsimsites-1))) {
	$once =1;
     } else {
	$once=0;
     }

     $first=1;
     $found=1;
     while ($found == 1)  {
      $found=0;
      if ($once == 0) {
	for ($sws=0;$sws<$nsws;$sws++) {
		if ($swused[$sws] == 0) {
			$swid = $swname[$sws];
			$found=1;
			last;
		}
	 }
      } else {
	if ($first == 1) {
		$found = 1;
		$first = 0;
	} else {
		$found = 0;
        }
      }

	# load Solid Waste Release files (one per wastesite and copc)
      if ($found == 1) {
	for ($sws=0;$sws<$nsws;$sws++) {
#	    if (($swname[$sws] eq $swid) || (($s == ($nsimsites-1)) && (($swused[$sws] == 0)))) {
	    if (($swname[$sws] eq $swid) && ($swused[$sws] == 0)) {
		# load file
             	printf(OL "Inserting Solid Waste site $swid $swcopc[$sws] $swname[$sws]\n");
		$swrf=$swrdir."/".$swname[$sws]."_".$swcopc[$sws].".csv";
        	open(SWR,"<$swrf") || die "Can't open $swrf file $!\n";
# skip 5 header lines
		for ($i=0;$i<5;$i++) {
			$line=<SWR>;
		}
# get units when Kevin put them in - $swunits
#                $swunits="(Ci/year)";

		# find rad column
		$swradcol = -1;
		for ($i=0;$i<$nsim2rad;$i++) {
			if ($sim2radname[$i]  eq $swcopc[$sws]) {
				$swradcol=$i;
			}
		}
		if ($swradcol == -1) {
			printf("Error - SWCOPC $swcopc[$sws] not found in header\n");
			exit(0);
		}

                $ns=0;
                while ($swline = <SWR>) {
                        chomp($swline);
			$line =~ s/\r//g;
                        @a=split(",",$swline);
                        $sl++;
                        $swyear = $a[0];
                        $swrate = $a[1];
                        if ((defined $swrate) && ($swrate ne "")
                                && (defined $swyear) && ($swyear ne "")) {
                                $swsly[$ns]=$swyear;
				$swrate = sprintf("%12.5e",$swrate);
                                $swslr[$ns]=$swrate;
                                $ns++;
                        }
                }
                close(SWR);
		$swimass=0.0;
                for ($k=0;$k<$ns-1;$k++) {
                        # calclate integrated mass in series
                        $c1=$swslr[$k];
                        $c2=$swslr[$k+1];
                        $y1=$swsly[$k];
                        $y2=$swsly[$k+1];
                        # mean conc over period
                        $ac=($c2+$c1)/2.0;
                        $dt=($y2-$y1);
                        $swimass=$swimass+($ac*$dt);
                }
                if ($swimass > 0) {
                  for ($ss=0;$ss<$ns;$ss++) {
        printf(OI "Solid Waste Release for $swcopc[$sws],,$swid,Solid Release Series,,$swsly[$ss],");
                                for ($k=0;$k<$swradcol;$k++) {
                                        printf(OI ",");
                                }
                                printf(OI "$swslr[$ss],\n");
                   }
                }
		$swused[$sws]=1;
		printf(OS "Solid Waste Release for $swcopc[$sws] Reduced Activity = $swredactivity[$sws],,$swid,Solid Release Integrated,,$swsly[0] to $swsly[$ns-1],");
		for ($k=0;$k<$swradcol;$k++) {
                     printf(OS ",");
                }
		printf(OS "%12.5e,\n",$swimass);
          }
	}
      } 
    }
  }
}

# Add any SAC Liquid - if in ehsit but not in SIM
for ($s=0;$s<$nsac;$s++) {
    # skip adding for tanks, except for C Tanks
    if (($sacname[$s] =~ m/241-/)  && (!$sacname[$s] =~ m/241-C-/i)) {
        printf(OL "Skipped check for SAC water for Tank waste sites (241-) = $sacname[$s]\n");
    } else {
	if (exists $ehsit_hash{$sacname[$s]}) {
	  if (exists $simv2_hash{$sacname[$s]}) {
# now - skip anything that has an entry in SIMV2
#		# check SIMV2 for liquid wastes at this year
#		# add if not
#                $sl = $simv2_hash{$sacname[$s]};
#                $nl = $simv2_count{$sacname[$s]};
#		$mflag = 0;
#		for($i=0;$i<$sacnyears[$s];$i++) {
#                    for ($j=0;$j<$nl;$j++) {
#                        @s = split(",",$slines[$sl+$j]);
#			printf("$sacname[$s]: SIMTIME = $s[$sim2timecol], SAC = $sacyear[$s][$i] ");
#			if ($s[$sim2timecol] == $sacyear[$s][$i]) {
#				printf("Matched\n");
#			} else {
#				printf("No Match\n");
#			}
#                        if ($s[$sim2timecol] == $sacyear[$s][$i]) {
#				# matched the year
#				$mflag=1;
#				last;
#			} 
#	            }
#		    if ($mflag == 1) {
#			# don't add this record
#			printf(OL "Not adding site $sacname[$s] from $liqinv to Inventory (already has a date match from SIMV2)\n");
#		    } else {
#			# add record - no date match in SIMV2 for this site
#			printf(OL "Adding $sacname[$s] from $liqinv to Inventory (in ehsit and SIMV2 but didn't match any dates)\n");
#			printf(OI "Liquid from $liqinv ($saclunit[$s][$i]),,$sacname[$s],Liquid,$sacliq[$s][$i],$sacyear[$s][$i],,,,,,,,,,,,,,,,,\n");
#			printf(OS "Liquid from $liqinv ($saclunit[$s][$i]),,$sacname[$s],Liquid,$sacliq[$s][$i],$sacyear[$s][$i],,,,,,,,,,,,,,,,,\n");
#		    }
#		}
	  } else {
	    printf(OL "Adding $sacname[$s] from $liqinv to Inventory (in ehsit but not in SIMV2)\n");
	    $sacsum=0;
	    for ($i=0;$i<$sacnyears[$s];$i++) {
	       printf(OI "Liquid from $liqinv ($saclunit[$s][$i]),,$sacname[$s],Liquid,$sacliq[$s][$i],$sacyear[$s][$i],,,,,,,,,,,,,,,,,\n");
		$sacsum+=$sacliq[$s][$i];
	       # update totals
	    }
	    $t=$sacnyears[$s]-1;
	    printf(OS "Total Liquid from $liqinv ($saclunit[$s][0]),,$sacname[$s],Liquid,$sacsum,$sacyear[$s][0] to $sacyear[$s][$t],,,,,,,,,,,,,,,,,\n");
	  }
	}
    } 
}

close(OI);
close(OL);
close(OS);
close(OX);
