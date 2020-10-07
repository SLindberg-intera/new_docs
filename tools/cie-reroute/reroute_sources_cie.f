c       ************************ PROGRAM reroute_source.f ****************************
c          Read SIM-V2 csv file and CIE chemical source csv file. Output rerouted CIE 
c          sources for the U-10 system, B-3 pond and T-4 Pond sites.
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      INTEGER yr
      DIMENSION val(17),sitevals(250,15,9),outvals(250,15,9)
      DIMENSION sitevol(250,15),totvol(250),ditvol(250)
      DIMENSION ditinf(250,4)
      DIMENSION fracinf(250,4),area(8)
      DIMENSION fracrate(250,15)
      DIMENSION ditval(250,4)
      DIMENSION u10(250),u10ovf(250),ovflow(250)
      DIMENSION ovfu9(250),ovfu11(250)
      CHARACTER infile1*256,infile2*256,infile3*256
      CHARACTER outfile1*80,outfile2*80,outfile3*80,outfile4*80
      CHARACTER im*80,simsite*80,casite*80,ciesite*80,st*80
      CHARACTER line*1024,sites(15)*15,dum1*8
      CHARACTER sitedat(15,4)*80,sitename*20,frmt*4
      CHARACTER(len=256), DIMENSION(:), allocatable :: args
c
      sitedat=""
      sitevol=0.0_8
      ditvol=0.0_8
      totvol=0.0_8
      ditinf=0.0_8
      fracinf=0.0_8
      fracrate=0.0_8
      sitevals=0.0_8
      outvals=0.0_8
      ditval=0.0_8
      u10ovf=0.0_8
      u10=0.0_8
      u10thr=7013071.9534295_8
      ovflow=0.0_8
      ovfu9=0.0_8
      ovfu11=0.0_8
c
c --- Read command line arguments
c
      num_args = command_argument_count()
      ALLOCATE(args(num_args))
      args=""
c
      DO ix = 1, num_args
        CALL get_command_argument(ix,args(ix))
      ENDDO
c
c --- Read SIMV2 csv filename
c
      READ(args(1),"(a256)") infile1
      WRITE(*,*) ' SIMV2 csv file = ',infile1
c
c --- Read CIE chemical csv filename
c
      READ(args(2),"(a256)") infile2
      WRITE(*,*) ' CIE chemical csv file = ',infile2
c
c --- Read B-3 Pond and T-4 Pond fractions filename
c
      READ(args(3),"(a256)") infile3
      WRITE(*,*) ' B-3 Pond and T-4 Pond fractions file = ',infile3
c
c --- Reroute sites
c
      sites=(/"216-Z-11","216-Z-19","216-Z-1D","216-U-14",
     >  "216-U-10","216-U-11","216-B-3 ","216-B-3A-RAD",
     >  "216-B-3B-RAD","216-B-3C-RAD","216-T-4A","216-T-4-1",
     >  "216-T-4B","216-T-4-2","216-T-4-2-SOUTH"/)
c
c --- Site areas for (in order): 216-Z-11,216-Z-19,216-Z-1Dtot,216-U-14tot,
c       216-U-10,216-U-11,216-Z-1Dsouth,216-U-14south
c
      area=(/658.304592447,650.081659045,4163.16491928,41007.6853106,
     >  194229.402893,67237.8559196,2144.24717683,20959.2514744/)
c
      outfile1="U-10_B-3_T-4_CIE_reroute_in.dat"
      outfile2="U-10_B-3_T-4_CIE_reroute_fractions.dat"
      outfile3="U-10_B-3_T-4_CIE_reroute_rates.dat"
      outfile4="U-10_B-3_T-4_CIE_reroute_rates.csv"
c
c --- Read yearly fractional rates for B-3 Pond sites and T-4 Pond sites.
c
      OPEN(13,FILE=infile3,STATUS='OLD'
     >  ,IOSTAT=IST)
      npyr=0
      READ(13,*)
   50 READ(13,*,END=60)ipyr,b3f,b3af,b3bf,b3cf,t4af,t41f,t4bf,t42f,t42sf
      npyr=ipyr-1943
      fracrate(npyr,7)=b3f
      fracrate(npyr,8)=b3af
      fracrate(npyr,9)=b3bf
      fracrate(npyr,10)=b3cf
      fracrate(npyr,11)=t4af
      fracrate(npyr,12)=t41f
      fracrate(npyr,13)=t4bf
      fracrate(npyr,14)=t42f
      fracrate(npyr,15)=t42sf
c
      GOTO 50
c
c --- Read SIMV2 rates for U-10 system sites, 216-B-3 and 216-T-4A.
c
   60 OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      minyr=1000000
      maxyr=-1000000
      READ(11,*)
      READ(11,*)
      READ(11,*)
      READ(11,*)
  100 READ(11,"(a1024)",END=150) line
      icnt=1
      DO iln=1,1024
        IF(line(iln:iln).eq." ") CYCLE
        IF(line(iln:iln).eq."/") CYCLE
        line(icnt:icnt)=line(iln:iln)
        icnt=icnt+1
      ENDDO
      line(icnt:icnt)=","
      DO iln=icnt+1,1024
        line(iln:iln)=" "
      ENDDO
      val=0.0_8
      READ(line,*) im,simsite,casite,st,val(1),yr,(val(ird),ird=2,17)
      keep=0
      DO ius=1,15
        dum1=TRIM(casite)
        IF(dum1.eq.sites(ius)) keep=ius
      ENDDO
      IF(keep.eq.0) GOTO 100
      IF(yr.lt.minyr) minyr=yr
      IF(yr.gt.maxyr) maxyr=yr
      indyr=yr-1943
      sitedat(keep,1)=im
      sitedat(keep,2)=simsite
      sitedat(keep,3)=casite
      sitedat(keep,4)=st
      sitevol(indyr,keep)=sitevol(indyr,keep)+val(1)
      totvol(indyr)=totvol(indyr)+val(1)
c
      sitevals(indyr,keep,1)=sitevals(indyr,keep,1)+val(1)
      sitevals(indyr,keep,2)=sitevals(indyr,keep,2)+val(4)
      sitevals(indyr,keep,3)=sitevals(indyr,keep,3)+val(5)
      sitevals(indyr,keep,4)=sitevals(indyr,keep,4)+val(8)
      sitevals(indyr,keep,5)=sitevals(indyr,keep,5)+val(9)
c
      GOTO 100
c
c --- Read CIE chemical rates for U-10 system sites, 216-B-3 and 216-T-4A.
c
  150 OPEN(12,FILE=infile2,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      WRITE(*,*) ' Opened chem file'
      READ(12,*)
  200 READ(12,"(a1024)",END=300) line
      icnt=1
      DO iln=1,1024
        IF(line(iln:iln).eq." ") CYCLE
        IF(line(iln:iln).eq."/") CYCLE
        line(icnt:icnt)=line(iln:iln)
        icnt=icnt+1
      ENDDO
      line(icnt:icnt)=","
      DO iln=icnt+1,1024
        line(iln:iln)=" "
      ENDDO
      val=0.0_8
      READ(line,*) im,simsite,ciesite,st,yr,(val(ird),ird=1,5)
      keep=0
      DO ius=1,15
        dum1=TRIM(ciesite)
        IF(dum1.eq.sites(ius)) keep=ius
      ENDDO
      IF(keep.eq.0) GOTO 200
      indyr=yr-1943
      IF(TRIM(sitedat(keep,3)).ne.TRIM(ciesite)) THEN
        WRITE(*,"(a27,2a20)") ' Unmatched CIE site name - ',
     >    TRIM(ciesite),TRIM(sitedat(keep,3))
        GOTO 9999
      ENDIF
c
      sitevals(indyr,keep,6)=sitevals(indyr,keep,6)+val(4)
      sitevals(indyr,keep,7)=sitevals(indyr,keep,7)+val(2)
      sitevals(indyr,keep,8)=sitevals(indyr,keep,8)+val(3)
      sitevals(indyr,keep,9)=sitevals(indyr,keep,9)+val(5)
c
      GOTO 200
c
c --- Open output files
c
  300 OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
      WRITE(20,"(9a)") '    ny    yr      z-11_influent',
     >  '      z-19_influent      z-1d_influent      u-14_influent',
     >  '             totvol',
     >  ' z-11_frac_influent z-19_frac_influent z-1d_frac_influent',
     >  ' u-14_frac_influent   z-11_frac_infilt',
     >  '   z-19_frac_infilt   z-1d_frac_infilt   u-14_frac_infilt',
     >  '      U-10&overflow        u-10_infilt      u-10_overflow',
     >  '   u-10_infilt_frac',
     >  '   u-11_infilt_frac'
c
      OPEN(21,FILE=outfile2,
     >  STATUS='REPLACE',IOSTAT=IST)
      WRITE(21,"(6a)") '    ny    yr   Z-11_frac_infilt',
     >  '   Z-19_frac_infilt   Z-1d_frac_infilt   U-14_frac_infilt',
     >  '   U-10_infilt_frac   U-11_infilt_frac    B-3_infilt_frac',
     >  '   B-3A_infilt_frac   B-3B_infilt_frac   B-3C_infilt_frac',
     >  '   T-4A_infilt_frac  T-4-1_infilt_frac   T-4B_infilt_frac',
     >  '  T-4-2_infilt_frac  T-4-2-S_infilt_frac'
c
      DO iyr=minyr,maxyr
        iiy=iyr-1943
c
c --- U-10 system calcs
c
        ditinf(iiy,1)=sitevol(iiy,1)
        ditinf(iiy,2)=sitevol(iiy,2)
        ditinf(iiy,3)=sitevol(iiy,3)
        ditinf(iiy,4)=sitevol(iiy,4)+sitevol(iiy,5)
        ditvol(iiy)=totvol(iiy)-sitevol(iiy,7)-sitevol(iiy,11)
        sumfrac=0.0_8
        DO ifr=1,4
          fracinf(iiy,ifr)=ditinf(iiy,ifr)/ditvol(iiy)
          sumfrac=sumfrac+fracinf(iiy,ifr)
        ENDDO
        IF(ABS(1.0-sumfrac).gt.1e-10) THEN
          WRITE(20,*) ' Ditch influent fractions do not sum to 1.0: ',
     >      sumfrac,iyr,iiy,ditinf(iiy,1),ditinf(iiy,2),ditinf(iiy,3),
     >      ditinf(iiy,4),ditvol(iiy)
          GOTO 9999
        ENDIF
        fracB3=sitevol(iiy,7)/totvol(iiy)
        fracT4=sitevol(iiy,11)/totvol(iiy)
        fracdit=(ditinf(iiy,1)+ditinf(iiy,2)+ditinf(iiy,3)+
     >    ditinf(iiy,4))/totvol(iiy)
        sumfrac=fracdit+fracB3+fracT4
        IF(ABS(1.0-sumfrac).gt.1e-10) THEN
          WRITE(20,*) ' Influent fractions do not sum to 1.0: ',sumfrac
          GOTO 9999
        ENDIF
c
c --------- Infiltration fraction for Z-11
c
        IF(ABS(fracinf(iiy,1)).gt.1e-10) THEN
          fracrate(iiy,1)=area(1)/(area(1)+(area(5)*fracinf(iiy,1)))
        ELSE
          fracrate(iiy,1)=0.0_8
        ENDIF
c
c --------- Infiltration fraction for Z-19
c
        IF(ABS(fracinf(iiy,2)).gt.1e-10) THEN
          fracrate(iiy,2)=area(2)/(area(2)+(area(5)*fracinf(iiy,2)))
        ELSE
          fracrate(iiy,2)=0.0_8
        ENDIF
c
c --------- Infiltration fraction for Z-1D
c
        IF(ABS(fracinf(iiy,3)).gt.1e-10) THEN
          IF(iyr.lt.1949) THEN
            az1d=area(3)
          ELSE
            az1d=area(7)
          ENDIF
          fracrate(iiy,3)=az1d/(az1d+(area(5)*fracinf(iiy,3)))
        ELSE
          fracrate(iiy,3)=0.0_8
        ENDIF
c
c --------- Infiltration fraction for U-14
c
        IF(ABS(fracinf(iiy,4)).gt.1e-10) THEN
          IF(iyr.lt.1985) THEN
            fracrate(iiy,4)=area(4)/(area(4)+(area(5)*fracinf(iiy,4)))
          ELSE
            fracrate(iiy,4)=1.0
          ENDIF
        ELSE
          fracrate(iiy,4)=0.0_8
        ENDIF
c
c --------- Calculate over flow fractions
c
        suminf=0.0_8
        DO infr=1,4
          suminf=suminf+ditinf(iiy,infr)*fracrate(iiy,infr)
        ENDDO
        u10ovf(iiy)=ditvol(iiy)-suminf
c
        IF(iyr.lt.1985) THEN
          IF(u10ovf(iiy).gt.u10thr) THEN
            u10(iiy)=u10thr
            ovflow(iiy)=u10ovf(iiy)-u10thr
          ELSE
            u10(iiy)=u10ovf(iiy)
            ovflow(iiy)=0.0_8
          ENDIF
        ELSE
          u10(iiy)=0.0_8
        ENDIF
c
        IF(u10ovf(iiy).gt.0.0_8) THEN
          fracrate(iiy,5)=u10(iiy)/u10ovf(iiy)
        ELSE
          fracrate(iiy,5)=0.0_8
        ENDIF
c
        IF(ovflow(iiy).gt.0.0_8) THEN
          fracrate(iiy,6)=ovflow(iiy)/u10ovf(iiy)
        ELSE
          fracrate(iiy,6)=0.0_8
        ENDIF
c
c --- Write output files
c
        WRITE(20,"(2i6,18es19.9)") iiy,iyr,
     >    (ditinf(iiy,idi),idi=1,4),ditvol(iiy),
     >    (fracinf(iiy,ifr),ifr=1,4),(fracrate(iiy,irc),irc=1,4),
     >    u10ovf(iiy),u10(iiy),ovflow(iiy),
     >    (fracrate(iiy,iof),iof=5,6)
c
c --- Write out fractions
c
        WRITE(21,"(2i6,15es19.9)") iiy,iyr,(fracrate(iiy,irc),irc=1,15)
c
      ENDDO
c
c --- Open rates output files
c
      OPEN(22,FILE=outfile3,
     >  STATUS='REPLACE',IOSTAT=IST)
      WRITE(22,"(7a)") 'Site                         Volume(m3)   Year',
     >  '                H-3              I-129              Sr-90',
     >  '              Tc-99                  U                 Cr',
     >  '                NO3                 CN'
c
      OPEN(23,FILE=outfile4,
     >  STATUS='REPLACE',IOSTAT=IST)
      WRITE(23,"(4a)") 'Inventory Module,SIMV2 site name,CIE site name',
     >  ',Source Type,Volume [m3],Discharge/decay-corrected year,H-3,',
     >  'I-129,Sr-90,Tc-99,U,Cr,NO3,CN,'
      WRITE(23,"(2a)") ',,,,m^3,year,Ci,Ci,Ci,Ci,kg,kg,kg,kg,'
c
c --- Calculate reroute rates
c
      DO ival=1,9
        ditval=0.0_8
        totval=0.0_8
        DO iyr=minyr,maxyr
          iiy=iyr-1943
          ditval(iiy,1)=sitevals(iiy,1,ival)
          ditval(iiy,2)=sitevals(iiy,2,ival)
          ditval(iiy,3)=sitevals(iiy,3,ival)
          ditval(iiy,4)=sitevals(iiy,4,ival)+sitevals(iiy,5,ival)
          totval=  ditval(iiy,1)+ditval(iiy,2)+ditval(iiy,3)+
     >      ditval(iiy,4)
c
c --- Set up output array: In order (1-15) - "216-Z-11","216-Z-19","216-Z-1D","216-U-14",
c       "216-U-10","216-U-11","216-B-3","216-B-3A-RAD","216-B-3B-RAD","216-B-3C-RAD",
c       "216-T-4A","216-T-4-1","216-T-4B","216-T-4-2","216-T-4-2-SOUTH"
c
          sumdit=0.0_8
c --- 216-Z-11
          outvals(iiy,1,ival)=ditval(iiy,1)*fracrate(iiy,1)
          sumdit=sumdit+outvals(iiy,1,ival)
c --- 216-Z-19
          outvals(iiy,2,ival)=ditval(iiy,2)*fracrate(iiy,2)
          sumdit=sumdit+outvals(iiy,2,ival)
c --- 216-Z-1D
          outvals(iiy,3,ival)=ditval(iiy,3)*fracrate(iiy,3)
          sumdit=sumdit+outvals(iiy,3,ival)
c --- 216-U-14
          outvals(iiy,4,ival)=ditval(iiy,4)*fracrate(iiy,4)
          sumdit=sumdit+outvals(iiy,4,ival)
c --- 216-U-10
          u10all=totval-sumdit
          outvals(iiy,5,ival)=u10all*fracrate(iiy,5)
c --- 216-U-11
          outvals(iiy,6,ival)=u10all*fracrate(iiy,6)
c --- 216-B-3
          outvals(iiy,7,ival)=sitevals(iiy,7,ival)*fracrate(iiy,7)
c --- 216-B-3A-RAD
          outvals(iiy,8,ival)=sitevals(iiy,7,ival)*fracrate(iiy,8)
c --- 216-B-3B-RAD
          outvals(iiy,9,ival)=sitevals(iiy,7,ival)*fracrate(iiy,9)
c --- 216-B-3C-RAD
          outvals(iiy,10,ival)=sitevals(iiy,7,ival)*fracrate(iiy,10)
c --- 216-T-4A
          outvals(iiy,11,ival)=sitevals(iiy,11,ival)*fracrate(iiy,11)
c --- 216-T-4-1
          outvals(iiy,12,ival)=sitevals(iiy,11,ival)*fracrate(iiy,12)
c --- 216-T-4B
          outvals(iiy,13,ival)=sitevals(iiy,11,ival)*fracrate(iiy,13)
c --- 216-T-4-2
          outvals(iiy,14,ival)=sitevals(iiy,11,ival)*fracrate(iiy,14)
c --- 216-T-4-2-SOUTH
          outvals(iiy,15,ival)=sitevals(iiy,11,ival)*fracrate(iiy,15)
c
        ENDDO
      ENDDO
c
c --- Write out reroute rates
c
      DO ius=1,15
        DO iyr=minyr,maxyr
          iiy=iyr-1943
          sitename=sites(ius)
          IF((ius.eq.3).and.(iyr.gt.1948)) sitename=
     >      TRIM(ADJUSTL(sites(ius)))//"-SOUTH"
          IF((ius.eq.4).and.(iyr.gt.1984)) sitename=
     >      TRIM(ADJUSTL(sites(ius)))//"-SOUTH"
          sumov=0.0_8
          DO iov=1,9
            sumov=sumov+outvals(iiy,ius,iov)
          ENDDO
          IF(ABS(sumov).gt.1e-15) THEN
            WRITE(22,"(a20,es19.9,i7,9es19.9)")
     >        ADJUSTR(sitename),outvals(iiy,ius,1),iyr,
     >        (outvals(iiy,ius,ival),ival=2,9)
c
            line=""
            WRITE(line,"(a9,a20,a15,es19.9,a1,i7,16(a1,es19.9))")
     >        'reroute,,',sitename,",Liquid,",outvals(iiy,ius,1),",",
     >        iyr,(",",outvals(iiy,ius,ival),ival=2,9)
            icw=1
            DO iln=1,1024
              IF(line(iln:iln).eq." ") CYCLE
              line(icw:icw)=line(iln:iln)
              icw=icw+1
            ENDDO
            DO iln=icw,1024
              line(iln:iln)=" "
            ENDDO
            WRITE(frmt,"(i4)") icw
            WRITE(23,"(a"//frmt//")") line(1:icw)
          ENDIF
        ENDDO
      ENDDO
c
 9999 CONTINUE
      STOP
      END
