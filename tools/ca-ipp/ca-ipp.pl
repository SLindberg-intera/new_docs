#!/usr/bsn/perl -w
# $RCSfile$ $Date$ $Author$ $Revision$
# ca-ipp.pl
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
#	Solid waste Release Directory (assumes "summary.csv" is there")
#	Redistribution File name (or none)
#	New Inventory File Name (prefix) and log file
#	
#	v4.0 new solid waste files

$dtstamp = localtime();

$vers="11/11/2019 Ver 4.0 by MDWilliams, Intera Inc.";

# Half Lives from EMDT-DE-0006 Rev 1, 18-May-2015
# Values in Years
$hlu232 = 68.9;
$hlu233 = 1.592e+005;
$hlu234 = 2.455e+005;
$hlu235 = 7.04e+008;
$hlu236 = 2.342e+007;
$hlu238 = 4.468e+009;
# Atomic Mass g/mol
# (https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=U)
# Accessed 5/14/2019
$amu232 = 232.0371563;
$amu233 = 233.0396355;
$amu234 = 234.0409523;
$amu235 = 235.0439301;
$amu236 = 236.0455682;
$amu238 = 238.0507884;
# calculate specific activities for U Isotopes (kg/Ci)
$curie = 3.7E+10;  # atoms per sec
$sau232 = ((log(2.0)*6.022E+23*1000.0)/($curie*($amu232)*($hlu232*365.25*24.0*60.0*60.0)));
$sau233 = ((log(2.0)*6.022E+23*1000.0)/($curie*($amu233)*($hlu233*365.25*24.0*60.0*60.0)));
$sau234 = ((log(2.0)*6.022E+23*1000.0)/($curie*($amu234)*($hlu234*365.25*24.0*60.0*60.0)));
$sau235 = ((log(2.0)*6.022E+23*1000.0)/($curie*($amu235)*($hlu235*365.25*24.0*60.0*60.0)));
$sau236 = ((log(2.0)*6.022E+23*1000.0)/($curie*($amu236)*($hlu236*365.25*24.0*60.0*60.0)));
$sau238 = ((log(2.0)*6.022E+23*1000.0)/($curie*($amu238)*($hlu238*365.25*24.0*60.0*60.0)));

#
$ehsit = shift @ARGV;
$radinv = shift @ARGV;
$cheminv = shift @ARGV;
$liqinv = shift @ARGV;
$swrdir = shift @ARGV;
$swrind = $swrdir."/summary.csv";
$redfn = shift @ARGV;
$outpref = shift @ARGV;
$outpref =~ s/[\r\n]+$//;
chomp($outpref);

$outlog=$outpref.".log";
$outinv=$outpref.".csv";
$outsum=$outpref."-summary.csv";

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

$dashes="----------------------------------------------------------------------";
printf(OL "Inventory preprocessor ca-ipp.pl Log File: $dtstamp\n");
printf(OL "# Processed by IPP $vers\n");
printf(OL "# ehsit file = $ehsit, Rad Inventory file = $radinv\n");
printf(OL "# Chemical Inventory file = $cheminv, SAC supplemental Liquids = $liqinv\n");
printf(OL "# Solid Waste Inventory Directory = $swrdir\n");
printf(OL "$dashes\n$dashes\n");

printf(OI "CA VZ Inventory: $dtstamp\n");
printf(OI "# Processed by IPP $vers\n");
printf(OI "# ehsit file = $ehsit, Rad Inventory file = $radinv\n");
printf(OI "# Chemical Inventory file = $cheminv, SAC supplemental Liquids = $liqinv\n");
printf(OI "# Solid Waste Inventory Directory = $swrdir\n\n");

printf(OS "# Inventory Summary for $outinv: $dtstamp\n");
printf(OS "# Processed by IPP $vers\n");
printf(OS "# ehsit file = $ehsit, Rad Inventory file = $radinv\n");
printf(OS "# Chemical Inventory file = $cheminv, SAC supplemental Liquids = $liqinv\n");
printf(OS "# Solid Waste Inventory Directory = $swrdir\n\n");

printf(OL "Calculated U232 Specific Activity (Ci/kg) = $sau232\n");
printf(OL "Calculated U233 Specific Activity (Ci/kg) = $sau233\n");
printf(OL "Calculated U234 Specific Activity (Ci/kg) = $sau234\n");
printf(OL "Calculated U235 Specific Activity (Ci/kg) = $sau235\n");
printf(OL "Calculated U236 Specific Activity (Ci/kg) = $sau236\n");
printf(OL "Calculated U238 Specific Activity (Ci/kg) = $sau238\n");

printf(OL "\n$dashes\n$dashes\n");
printf(OL "Loading $ehsit\n");
# load ehsit (shapefile of waste sites, converted to csv)
# skip header
$line = <SG>;
$nhsit=0;
while ($line = <SG>) {
    chomp($line);
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
printf(OI "# Inventory File Header = $line\n\n");
printf(OS "# Inventory File Header = $line\n\n");
printf(OL "# Inventory File Header = $line\n\n");

# load header - 2 lines (units and rads)
$line = <SR>;
chomp($line);

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
# printf(OI "$line\n");
@hu=split(",",$line);

#find year, volume, site, source, and units columns
$nhu=scalar(@hu);
$sim2volunits="";
for ($i=0;$i<$nhu;$i++) {
	if (lc($hu[$i]) =~ m/ca site name/) {
		$casitecol = $i;
	} elsif (lc($hu[$i]) =~ m/simv2 site name/) {
		$sim2sitecol = $i;
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

# find rad columns
#$line = <SR>;
#chomp($line);
@hr=split(",",$line);
$nhr=scalar(@hr);
$ntrad = $nhr - 6;
printf("NTRAD = $ntrad, $line\n");
$nsim2rad=0;
$u232col=-1;
for ($i=0;$i<$ntrad;$i++) {
	# remove any parantheticals (space after name)
	@a = split(" ",$hr[6+$i]);
	$s2r = $a[0];
	# remove leading and trailing spaces
	if (defined $s2r) {
	    $s2r =~ s/^\s+|\s+$//g;
	    if ($s2r =~ m/U-232/i) {
		$u232col=6+$i;
	    }
	    $sim2radname[$nsim2rad]=$s2r;
	    $nsim2rad++;
	}
}
if ($u232col != -1) {
	$u233col=$u232col+1;
	$u234col=$u232col+2;
	$u235col=$u232col+3;
	$u236col=$u232col+4;
	$u238col=$u232col+5;
} else {
	printf("Error - Could not find U-232 in Rad Header\n");
	exiti();
}

# create columns for Chems and total uranium in kg
$nchem=4;
$ucol=$nsim2rad+6;
$chemname[0]="U";
$chemunits[0]="kg";
$crcol=$ucol+1;
$chemname[1]="Cr";
$chemunits[1]="kg";
$no3col=$ucol+2;
$chemname[2]="NO3";
$chemunits[2]="kg";
$cncol=$ucol+3;
$chemname[3]="CN";
$chemunits[3]="kg";

printf(OI "$hu[0],$hu[1],$hu[2],$hu[3],$hu[4],$hu[5],");
printf(OS "$hu[0],$hu[1],$hu[2],$hu[3],$hu[4],$hu[5],");
for ($i=0;$i<$nsim2rad;$i++) {
	printf(OI "$sim2radname[$i],");
	printf(OS "$sim2radname[$i],");
}
for ($i=0;$i<$nchem;$i++) {
	printf(OI  "$chemname[$i],");
	printf(OS  "$chemname[$i],");
}
printf(OI "\n");
printf(OS "\n");
printf(OI ",,,,$sim2volunits,$sim2timeunit,");
printf(OS ",,,,$sim2volunits,$sim2timeunit,");
for ($i=0;$i<$nsim2rad;$i++) {
        printf(OI "$sim2radunits,");
	printf(OS "$sim2radunits,");
}
for ($i=0;$i<$nchem;$i++) {
        printf(OI "$chemunits[$i],");
	printf(OS "$chemunits[$i],");
}
printf(OI "\n");
printf(OS "\n");

my %yearh;
my %swidh;
@simv2_hash = {};
@simv2_count = {};
$il=0;
$nsimsites=0;
while ($line=<SR>) {
	# load sim inventory
	chomp($line);
	$slines[$il]=$line;
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

	    if (exists $simv2_hash{$swid}) {
		$simv2_count{$swid}++;
            } else {
		$simv2_site[$nsimsites]=$swid;
		$nsimsites++;
                $simv2_hash{$swid} = $il;
		$simv2_count{$swid} = 1;
            }

	    # Calculate U (kg)
#	    $ncols=scalar(@yl);
	    $ncommas= () = $slines[$il] =~ /,/gi;
#printf("ncols,ncommas,ucol=$ncols,$ncommas,$ucol\n");
#printf("$slines[$il]\n");
	    if ($ncommas > $ucol) {
		printf("Error - too many columns b4 adding U\n");
		exit();
	    } 
	    if ($ncommas < $ucol) {
		for ($i=0;$i<($ucol-($ncommas+1));$i++) {
			$slines[$il]=$slines[$il].",";
		}
	    }
	    $u=0.0;
	    if ((exists($yl[$u232col])) && ($yl[$u232col] ne "")) {
		$u=$u+$yl[$u232col]/$sau232;
	    }
            if ((exists($yl[$u233col])) && ($yl[$u233col] ne "")) {
                $u=$u+$yl[$u233col]/$sau233;
            }
            if ((exists($yl[$u234col])) && ($yl[$u234col] ne "")) {
                $u=$u+$yl[$u234col]/$sau234;
            }
            if ((exists($yl[$u235col])) && ($yl[$u235col] ne "")) {
                $u=$u+$yl[$u235col]/$sau235;
            }
            if ((exists($yl[$u236col])) && ($yl[$u236col] ne "")) {
                $u=$u+$yl[$u236col]/$sau236;
            }
            if ((exists($yl[$u238col])) && ($yl[$u238col] ne "")) {
                $u=$u+$yl[$u238col]/$sau238;
            }
	    if ($u>0.0) {
		$slines[$il]=$slines[$il].",".sprintf("%12.5e",$u);
	    } else {
		$slines[$il]=$slines[$il].",";
	    }

	    $il++;
	}
}
close(SR);
# load CHEM Inventory (if exists);
if ($cheminv ne "none") {
        printf(OL "\n$dashes\n$dashes\n");
        printf(OL "Loading $cheminv - merging with Rad Inventory\n");

	# skip header lines
	$line = <SC>;
	$line = <SC>;
	$line = <SC>;
	while ($line = <SC>) {
	  chomp($line);
	  $line =~ s/\r//g;
 	  @a=split(",",$line);
	  $cswid=uc($a[1]);
          $cswid =~ tr/\"//d;
          $cswid =~ s/^\s+|\s+$//g;
	  $cyear=$a[3];
	  if ((exists($a[4])) && ($a[4] ne "")) {
		$ccr=$a[4];
	  } else {
		$ccr=0.0;
	  }
	  if ((exists($a[5])) && ($a[5] ne "")) {
		$cno3=$a[5];
	  } else {
		$cno3=0.0;
	  }
	  if ((exists($a[6])) && ($a[6] ne "")) {
		$ccn=$a[6];
	  } else {
		$ccn=0.0;
	  }
	  if ($cyear > 0.0) {
	    # find match in Rad Inventory
	    if (exists $simv2_hash{$cswid}) {
		$sl = $simv2_hash{$cswid};
		$nl = $simv2_count{$cswid};
		$mflag = -1;
		for ($i=0;$i<$nl;$i++) {
		    @s = split(",",$slines[$sl+$i]);
		    if ($s[5] == $cyear) {
			$mflag=$sl+$i;
			# update with chems
			if ($ccr > 0.0) {
				if ((exists($s[$crcol])) && ($s[$crcol] > 0.0)) {
					$s[$crcol]=$s[$crcol]+$ccr;
				} else {
					$s[$crcol]=$ccr;
				}
			}
                        if ($cno3 > 0.0) {
                                if ((exists($s[$no3col])) && ($s[$no3col] > 0.0)) {
                                        $s[$no3col]=$s[$no3col]+$cno3;
                                } else {
                                        $s[$no3col]=$cno3;
				}
                        }
                        if ($ccn > 0.0) {
                                if ((exists($s[$cncol])) && ($s[$cncol] > 0.0)) {
                                        $s[$cncol]=$s[$cncol]+$ccn;
                                } else {
                                        $s[$cncol]=$ccn;
				}
                        }
			# build line again
			$tline="";
			for ($j=0;$j<=$cncol;$j++) {
				if ((exists($s[$j])) && ($s[$j] ne "")) {
					$tline=$tline.$s[$j].",";
				} else {
					$tline=$tline.",";
				}
			}
			$slines[$sl+$i]=$tline;
		    }
		}
		if ($mflag == -1) {
			printf("Error - Can't find chem/year in simv2: $cswid, $cyear\n");
		}
	    } else {
		printf("Error - $cswid (chem) not in simv2\n");
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
                @yl=split(",",$line);
                $year[$i]=$yl[0];
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
    printf(OL "Rerouting Sources based on $redfn\n");
    # load files
    while ($rdfn = <RF>) {
        chomp($rdfn);
        printf(OL "Replacing / supplementing Sources based on $rdfn\n");
        open(RDF,"<$rdfn") || die "Can't open $rdfn file $!\n";
        # two header lines
        for ($i=0;$i<2;$i++) {
                $line = <RDF>;
        }
        $lastsite="";
        while ($line = <RDF>) {
                chomp($line);
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
	    # Calculate U (kg)
	    $u=0.0;
	    @yl = @a;
	    if ((exists($yl[$u232col])) && ($yl[$u232col] ne "")) {
                $u=$u+$yl[$u232col]/$sau232;
            }
            if ((exists($yl[$u233col])) && ($yl[$u233col] ne "")) {
                $u=$u+$yl[$u233col]/$sau233;
            }
            if ((exists($yl[$u234col])) && ($yl[$u234col] ne "")) {
                $u=$u+$yl[$u234col]/$sau234;
            }
            if ((exists($yl[$u235col])) && ($yl[$u235col] ne "")) {
                $u=$u+$yl[$u235col]/$sau235;
            }
            if ((exists($yl[$u236col])) && ($yl[$u236col] ne "")) {
                $u=$u+$yl[$u236col]/$sau236;
            }
            if ((exists($yl[$u238col])) && ($yl[$u238col] ne "")) {
                $u=$u+$yl[$u238col]/$sau238;
            }
	    if ($u > 0.0) {
		# rebuild line
		$yl[$ucol]=$u;
		$line="";
		for ($i=0;$i<scalar(@yl);$i++) {
			$line=$line.$yl[$i].",";
		}
	    }

                printf(OL "Reroute: $line\n");
                $slines[$il]=$line;
		$il++;
                $simv2_count{$rsit}++;
                $lastsite = $rsit;
	}
    }
}
printf(OL "\n$dashes\n$dashes\n");

# load Solid Waste Sites
# read index - skip header
$nsws=0;
$nswsites=0;
if ($swrdir ne "none") {
  printf(OL "Loading Solid Waste Release Site Index $swrind\n");
  $line = <SWI>;
  $nsws=0;
  $nswsites=0;
  @sws_hash = {};
  while ($line = <SWI>) {
        chomp($line);
        @a=split(",",$line);
        $swname[$nsws]=$a[1];
        $swfile[$nsws]=$a[7];
# replace any \ with / (DOS convention)
	$swfile[$nsws] =~ s/\\/\//g;
	$swcopc[$nsws]=$a[0];
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
	if (($swsflag == 1) && (lc($yltype) =~ /olid/)) {
	    # pitch line if a solid, will replace with release
#	    printf("  Yes!\n");
	    printf(OL "Solid Inventory Skipped, Replaced by Release: $line\n");

	} else {
#	    printf("  No!\n");
	    # Calculate total U from isotopes


            # write out line
            printf(OI "$line\n");

            # add to totals
	    if ($flag == 0) {
		$flag = 1;
		@tot = split(",",$line);
		$tot[0]="Total";
		$tot[$sim2sourcecol]="";
		$tot[$sim2volcol]=0;
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

    # insert solid waste release
    if ($swsflag == 1) {
	# load Solid Waste Release files (one per wastesite and copc)
	for ($sws=0;$sws<$nsws;$sws++) {
	    if ($swname[$sws] eq $swid) {
			# load file
             	printf(OL "Inserting Solid Waste site $swid $swcopc[$sws] $swfile[$sws]\n");
		$swrf=$swrdir."/".$swfile[$sws];
        	open(SWR,"<$swrf") || die "Can't open $swrf file $!\n";

# get units when Kevin put them in - $swunits
                $swunits="(Ci/year)";

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

        	# skip header
                $swline=<SWR>;
                $ns=0;
                while ($swline = <SWR>) {
                        chomp($swline);
                        @a=split(",",$swline);
                        $sl++;
                        $swyear = $a[4];
                        $swrate = $a[5];
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
		printf(OS "Solid Waste Release for $swid not integrated yet\n");
	}
    }
}

    # print total
    for ($i=0;$i<5;$i++) {
    	printf(OS "$tot[$i],");
    }
    printf(OS "$tottmin to $tottmax,");
    for ($i=0;$i<$ntrad+$nchem;$i++) {
	if (defined $tot[6+$i]) {
	    printf(OS "$tot[6+$i],");
	} else {
	    printf(OS ",");
        }
    }
    printf(OS "\n");
	
}

# Add any SAC Liquid - if in ehsit but not in SIM
for ($s=0;$s<$nsac;$s++) {
	if ((exists $ehsit_hash{$sacname[$s]}) && (!exists $simv2_hash{$sacname[$s]})) {
	    printf(OL "Adding $sacname[$s] from $liqinv to Inventory (in ehsit but not in SIMV2)\n");
	    for ($i=0;$i<$sacnyears[$s];$i++) {
	       printf(OI "Liquid from $liqinv ($saclunit[$s][$i]),,$sacname[$s],Liquid,$sacliq[$s][$i],$sacyear[$s][$i],,,,,,,,,,,,,,,,,\n");
	       # update totals
	    }
	}
}

# Add any Solid Waste Sites not in SIMV2
for ($sws=0;$sws<$nsws;$sws++) {
        if ($swused[$sws] == 0) {
		$swid = $swname[$sws];
                # load file
                printf(OL "Inserting Solid Waste site $swid $swfile[$sws] $swcopc[$sws]\n");
                $swrf=$swrdir."/".$swfile[$sws];
                open(SWR,"<$swrf") || die "Can't open $swrf file $!\n";
                # find rad column

# get units when Kevin put them in - $swunits
		$swunits="(Ci/year)";
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

                # skip header
                $swline=<SWR>;
		$ns=0;
                while ($swline = <SWR>) {
                        chomp($swline);
			@a=split(",",$swline);
                        $sl++;
                        $swyear = $a[4];
                        $swrate = $a[5];
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
                printf(OS "Solid Waste Release for $swid not integrated yet\n");
	}
}


close(OI);
close(OL);
close(OS);
