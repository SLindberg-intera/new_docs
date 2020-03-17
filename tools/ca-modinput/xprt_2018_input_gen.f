c       ************************ PROGRAM xprt_2018_input_gen.f ****************************
c          Reads SS input file and modifies for the 1943-2018 transport simulation.
c
c          Command line variables:
c             1) Rad Group - rad1 or rad2
c             2) Area - 200E or 200W
c             3) Buffer - Enter "buffer" if the model has a buffer; "nobuffer" if not
c             4) Path to the file containing the 200 West Area material properties
c             5) Path to the file containing the 200 East Area material properties
c             6) Path to the file containing the radiolnuclide group 1 (C-14, Cl-36, H-3, I-129, Np-237, Re-187, Sr-90 and Tc-99) solute properties
c             7) Path to the file containing the radiolnuclide group 2 (U 232, U 233, U 234, U 235, U 236, U 238, Th-230 and Ra-226) solute properties
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      INTEGER tops(500,500)
	  DIMENSION propmat(25,3),propsol(25,4)
      CHARACTER infile1*80,infile2*80,infile3*80,infile4*80,infile5*80
      CHARACTER infile6*80,infile7*80,infile8*80,infile9*80,outfile1*80
      CHARACTER WMATTR*80,EMATTR*80,R1SOLTR*80,R2SOLTR*80
      CHARACTER line1*1024,dum1*10,dum2*10,ewarea*4,radgrp*4
      CHARACTER frmt*10,bcn*10,zonelist(25)*25,buff*8
	  CHARACTER matname(25)*25,solname(25)*25
      CHARACTER(len=80), DIMENSION(:), allocatable :: args
c
      irad=0
      izone=0
      nzone=0
      tops=0
	  matname=""
	  propmat=-1000000.0
	  solname=""
	  propsol=-1000000.0
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
      WRITE(*,*) ' num_args = ',num_args
c
c --- Read rad group from the command line arguments
c
      READ(args(1),*) radgrp
      IF(radgrp.eq."rad1") THEN
        irad=1
      ELSEIF(radgrp.eq."rad2") THEN
        irad=2
      ELSE
        WRITE(*,*) ' Invalid radionuclide group = ',radgrp
        GOTO 9999
      ENDIF
      WRITE(*,*) ' Rad group = ',irad
c
c --- Read model area (200E or 200W) from the command line arguments
c
      READ(args(2),*) ewarea
      WRITE(*,*) ' Model Area = ',ewarea
c
c --- Read buffer switch from the command line arguments
c
      READ(args(3),*) buff
      WRITE(*,*) ' buffer = ',buff
      IF(buff(1:6).eq."buffer") THEN
        ibuff=1
        WRITE(*,*) ' Aqueous-only buffer will be read'
      ELSE
        ibuff=0
        WRITE(*,*) ' Aqueous-only buffer will not be read'
      ENDIF
c
c --- Read properties file names
c
      READ(args(4),"(a80)") WMATTR
      READ(args(5),"(a80)") EMATTR
      READ(args(6),"(a80)") R1SOLTR
      READ(args(7),"(a80)") R2SOLTR
c
      WRITE(*,*)
c
      nyrend=2018
c
      infile1="../ss/input_SS"
      infile2="../ret/ca_tr_boundary_card.dat"
      IF(ewarea.eq."200W") THEN
        infile3=WMATTR
      ELSEIF(ewarea.eq."200E") THEN
        infile3=EMATTR
      ELSE
        WRITE(*,*) ' Area ',ewarea,' is not a valid option.'
        GOTO 9999
      ENDIF
      infile7="../sources/buffer-aq-src.card"
      infile8="../build/input.top"
      IF(irad.eq.1) THEN
        infile4="../trOCcards/rad1_Output_Control.dat"
        infile5="../trsurfcards/rad1_surface_flux.txt"
        infile6="../sources/rads1-src.card"
        infile9=R1SOLTR
        IF(ibuff.eq.1) THEN
          outfile1="input_XPRT-1_2018_with_buffer"
        ELSE
          outfile1="input_XPRT-1_2018_no_buffer"
        ENDIF
      ELSEIF(irad.eq.2) THEN
        infile4="../trOCcards/rad2_Output_Control.dat"
        infile5="../trsurfcards/rad2_surface_flux.txt"
        infile6="../sources/rads2-src.card"
        infile9=R2SOLTR
        IF(ibuff.eq.1) THEN
          outfile1="input_XPRT-2_2018_with_buffer"
        ELSE
          outfile1="input_XPRT-2_2018_no_buffer"
        ENDIF
      ELSE
        WRITE(*,*) ' Rad group = ',irad,' End script'
        GOTO 9999
      ENDIF
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- Read top k values for each i,j
c
      OPEN(18,FILE=infile8,STATUS='OLD'
     >  ,IOSTAT=IST)
c
   10 READ(18,*,END=20) itp,jtp,ktp
      tops(itp,jtp)=ktp
      GOTO 10
c
c --- Read material transport parameters
c
   20 OPEN(13,FILE=infile3,STATUS='OLD'
     >  ,IOSTAT=IST)
      READ(13,*)
c
      nmprop=1
   30 READ(13,"(a25,3f20.1)",END=40) matname(nmprop),
     >  (propmat(nmprop,nprp),nprp=1,3)
      nmprop=nmprop+1
      GOTO 30
   40 nmprop=nmprop-1
c
c --- Read solute transport parameters
c
      OPEN(19,FILE=infile9,STATUS='OLD'
     >  ,IOSTAT=IST)
      READ(19,*)
c
      nsprop=1
   50 READ(19,"(a25,f20.1,e20.3,2e20.1)",END=60) solname(nsprop),
     >  (propsol(nsprop,nprp),nprp=1,4)
      nsprop=nsprop+1
      GOTO 50
   60 nsprop=nsprop-1
c
c --- Find first and last years for source domain sites
c
      OPEN(16,FILE=infile6,STATUS='OLD'
     >  ,IOSTAT=IST)
      initsl=1000000
      lastsl=0
      initaq=1000000
      lastaq=0
   70 READ(16,"(a1024)",END=75) line1
      DO ic=1,200
        IF(line1(ic:ic+5).eq."Solute") THEN
          READ(line1(ic+1:256),*) dum1,dum2,i1,i2,j1,j2,k1,k2,ny
          DO iy=1,ny
            READ(16,*) iyr
            IF(iyr.lt.initsl) initsl=iyr
            IF(iyr.gt.lastsl) lastsl=iyr
          ENDDO
        ENDIF
      ENDDO
c
      DO ic=1,200
        IF(line1(ic:ic+17).eq."Aqueous Volumetric") THEN
          READ(line1(ic+19:256),*) i1,i2,j1,j2,k1,k2,ny
          DO iy=1,ny
            READ(16,*) iyr
            IF(iyr.gt.lastaq) lastaq=iyr
            IF(iyr.lt.initaq) initaq=iyr
          ENDDO
        ENDIF
      ENDDO
c
      GOTO 70
c
   75 CLOSE(16)
c
c --- Find first and last years for buffer domain sites
c
      IF(ibuff.eq.1) THEN
        OPEN(17,FILE=infile7,STATUS='OLD'
     >    ,IOSTAT=IST)
   80   READ(17,"(a1024)",END=90) line1
        DO ic=1,200
          IF(line1(ic:ic+5).eq."Solute") THEN
            READ(line1(ic+7:256),*) dum1,i1,i2,j1,j2,k1,k2,ny
            DO iy=1,ny
              READ(17,*) iyr
              IF(iyr.lt.initsl) initsl=iyr
              IF(iyr.gt.lastsl) lastsl=iyr
            ENDDO
          ENDIF
        ENDDO
c
        DO ic=1,200
          IF(line1(ic:ic+17).eq."Aqueous Volumetric") THEN
            READ(line1(ic+19:256),*) i1,i2,j1,j2,k1,k2,ny
            DO iy=1,ny
              READ(17,*) iyr
              IF(iyr.gt.lastaq) lastaq=iyr
              IF(iyr.lt.initaq) initaq=iyr
            ENDDO
          ENDIF
        ENDDO
c
        GOTO 80
c
   90   CLOSE(17)
      ENDIF
c
      inityr=MIN(initaq,initsl)
      lastyr=MAX(lastaq,lastsl)
c
      WRITE(*,*) ' First aqueous year = ',initaq
      WRITE(*,*) ' Last aqueous year = ',lastaq
      WRITE(*,*) ' First solute year = ',initsl
      WRITE(*,*) ' Last solute year = ',lastsl
      WRITE(*,*) ' First source year = ',inityr
      WRITE(*,*) ' Last source year = ',lastyr
c
c --- Read SS input file and revise for rad transport input
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
  100 READ(11,"(a1024)",END=9991) line1
      DO ii=1,1024
        IF(line1(ii:ii+21).eq.'~Simulation Title Card') GOTO 200
      ENDDO
      GOTO 100
c
  200 WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
  210 READ(11,"(a1024)",END=9992) line1
      DO ii=1,1024
        IF(line1(ii:ii+5).eq.'Steady') GOTO 300
        IF(line1(ii:ii).eq.'~') GOTO 9992
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 210
c
  300 IF(nyrend.lt.10000) THEN
        WRITE(frmt,"(i5)") 4
      ELSE
        WRITE(frmt,"(i5)") 5
      ENDIF
      IF(irad.eq.1) THEN
        WRITE(20,"(a26,a6,i"//frmt//",a2)") 
     >    'Rad1 Transport Simulation ',
     >    '(1943-',nyrend,'),'
      ELSE
        WRITE(20,"(a26,a6,i"//frmt//",a2)") 
     >    'Rad2 Transport Simulation ',
     >    '(1943-',nyrend,'),'
      ENDIF
  310 READ(11,"(a1024)",END=9993) line1
      DO ii=1,1024
        IF(line1(ii:ii+21).eq.'~Solution Control Card') GOTO 400
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 310
c
  400 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)") 'Restart File, ../ss/restart,'
      WRITE(20,"(a)") 'Water w/ Patankar Vadose Transport Courant,1.0,'
      IF(lastaq.eq.0) THEN
        WRITE(20,"(a)") '1,'
      ELSEIF(lastaq.lt.2018) THEN
        WRITE(20,"(a)") '3,'
      ELSE
        WRITE(20,"(a)") '2,'
      ENDIF
c
      IF(lastaq.eq.0) THEN
        WRITE(20,"(i4,a6,i4,a43)") 1943,',year,',
     >    2018,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
      ELSE
        WRITE(20,"(i4,a6,i4,a43)") 1943,',year,',
     >    inityr,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
c
        IF(lastaq.lt.2018) THEN
          WRITE(20,"(i4,a6,i4,a44)") inityr,',year,',
     >      lastaq,',year,1.0E-08,year,0.01,year,1.25,16,1.0E-6,'
          WRITE(20,"(i4,a6,i4,a43)") lastaq,',year,',
     >      2018,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
        ELSE
          WRITE(20,"(i4,a6,i4,a44)") inityr,',year,',
     >      2018,',year,1.0E-08,year,0.01,year,1.25,16,1.0E-6,'
        ENDIF
      ENDIF
c
      WRITE(20,"(a)") '1000000,'
      WRITE(20,"(a)") '0,'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
  410 READ(11,"(a1024)",END=9994) line1
      DO ii=1,1024
        IF(line1(ii:ii+19).eq.'~Grid Card') GOTO 500
      ENDDO
      GOTO 410
c
  500 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
  510 READ(11,"(a1024)",END=9995) line1
c
      iskip=0
      DO ii=1,1024
        IF(line1(ii:ii+23).eq.'~Rock/Soil Zonation Card') izone=1
        IF(line1(ii:ii+26).eq.'~Mechanical Properties Card') izone=2
      ENDDO
      IF(izone.eq.1) THEN
        DO ii=1,1024
          IF(line1(ii:ii+22).eq.'Zonation File Formatted') iskip=1
          IF(line1(ii:ii+22).eq.'#-----------') iskip=1
        ENDDO
        IF(iskip.eq.0) THEN
          izlen=0
          DO ii=1,1024
            IF(line1(ii:ii).eq.',') izlen=ii
          ENDDO
          IF(izlen.gt.0) THEN
            nzone=nzone+1
            zonelist(nzone)=line1(1:izlen-1)
            WRITE(*,*) ' Zone ',nzone,' = ',zonelist(nzone)
          ENDIF
        ENDIF
      ENDIF
c
      DO ii=1,1024
        IF(line1(ii:ii+23).eq.'~Initial Conditions Card') GOTO 600
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 510
c
c --- Add Solute/Fluid and Solute/Porous Media Cards
c
  600 CONTINUE
      WRITE(20,"(a30)") '~Solute/Fluid Interaction Card'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(i1,a1)") nsprop,','
	  DO isn=1,nsprop
        WRITE(20,"(a6,a15,es8.2e1,a20,es10.3e2,a5,es8.1e2,a9)")
     >    TRIM(solname(isn)),', Conventional,',propsol(isn,3),
     >    ', m^2/s, continuous,',propsol(isn,2),', yr,',
     >    propsol(isn,4),', Ci/m^3,'
        ENDDO
      IF(irad.eq.1) THEN
        WRITE(20,"(a)") '0,'
      ELSE
        WRITE(20,"(a)") '2,'
        WRITE(20,"(a)") ' U-234, Th-230, 1.00,'
        WRITE(20,"(a)") ' Th-230, Ra-226, 1.00,'
      ENDIF
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
      WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a37)") '~Solute/Porous Media Interaction Card'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      DO izn=1,nzone
        iznnmp=0
        DO imn=1,nmprop
          IF(zonelist(izn).eq.matname(imn)) iznnmp=imn
        ENDDO
        IF(iznnmp.eq.0) THEN
          WRITE(*,*) trim(zonelist(izn)),
     >      ' not found in material transport properties file'
          GOTO 9999
        ENDIF
        llen=len(trim(zonelist(izn)))
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//",a1,f4.1,a4,f5.2,a4)") zonelist(izn),
     >    ',',propmat(iznnmp,1),', m,',propmat(iznnmp,2),', m,'
        DO isn=1,nsprop
          IF(propsol(isn,1).ge.10.0_8) THEN
            gckd=(1.0_8-propmat(iznnmp,3)/100.0_8)*propsol(isn,1)+
     >        (propmat(iznnmp,3)/100.0_8)*0.23_8*propsol(isn,1)
          ELSE
            gckd=(1.0_8-propmat(iznnmp,3)/100.0_8)*propsol(isn,1)
          ENDIF
          WRITE(20,"(a7,a1,es9.2,a8)") TRIM(solname(isn)),',',
     >      gckd,', mL/g,,'
        ENDDO
      ENDDO
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
c --- Replace Initial Conditions Card
c
      WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a24)") '~Initial Conditions Card'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)") 'Gas Pressure, Aqueous Pressure,'
      WRITE(20,"(a)") '0,'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
  610 READ(11,"(a1024)",END=9996) line1
      DO ii=1,1024
        IF(line1(ii:ii+24).eq.'~Boundary Conditions Card') GOTO 700
      ENDDO
      GOTO 610
c
c --- Replace SS RET with transient RET
c
  700 OPEN(12,FILE=infile2,STATUS='OLD'
     >  ,IOSTAT=IST)
      llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
      WRITE(20,"(2a)") '#------------------------',
     >  '------------------------------------------'
  710 READ(12,"(a1024)",END=9997) line1
      IF(line1(1:1).ne.'#') GOTO 720
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 710
c
  720 READ(line1,*) nbc
      WRITE(bcn,"(i5)") nbc+1
      llen=len(trim(ADJUSTL(bcn)))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//",a1)") ADJUSTL(bcn),','
  730 READ(12,"(a1024)",END=800) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 730
c
  800 WRITE(20,"(2a)") 'file, input.bot, Dirichlet Aqueous, outflow, ',
     >  'outflow, outflow, outflow, outflow, outflow, outflow, outflow,'
      WRITE(20,"(a)") '1,'
      WRITE(20,"(a)") '1943,year,101325,Pa,,,,,,,,,,,,,,,,,'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)")
c
c --- Replace SS output control with rad output control
c
      OPEN(14,FILE=infile4,STATUS='OLD'
     >  ,IOSTAT=IST)
  810 READ(14,"(a1024)",END=900) line1
      DO ii=1,1024
        IF(line1(ii:ii+9).eq.'No Restart') THEN
          line1="Final Restart, ,"
          EXIT
        ENDIF
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 810
c
  900 WRITE(20,"(a)")
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
c
c --- Replace SS surface flux with rad surface flux
c
      OPEN(15,FILE=infile5,STATUS='OLD'
     >  ,IOSTAT=IST)
      numsrftot=0
c
      READ(15,*)
  940 READ(15,"(a1024)",END=1000) line1
      IF((line1(1:1).ne."#").and.(line1(1:1).ne."~")) GOTO 950
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 940
c
  950 READ(line1,*) nsrf
      nsrf=(nsrf-9)*2+9
      WRITE(20,"(i5,a1)") nsrf,','
c
  955 READ(15,"(a1024)",END=960) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 955
c
  960 REWIND(15)
  965 READ(15,"(a1024)") line1
      IF(line1(1:15).eq."9, srf/modflow_") THEN
        BACKSPACE(15)
        GOTO 970
      ENDIF
      GOTO 965
c
  970 READ(15,"(a1024)",END=1000) line1
      mintop=1000000
      DO iji=1,100
        IF(line1(iji:iji+4).eq.".srf,") THEN
c          WRITE(20,*) ' iji=',iji
          EXIT
        ENDIF
      ENDDO
      WRITE(frmt,"(i5)") iji-1
      WRITE(20,"(a"//frmt//",a9)") line1,'_top.srf,'
      READ(15,"(a1024)",END=1000) line1
      READ(line1(29:50),*) jrp2r,icp2r
      llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen-7
c      WRITE(20,"(a10,i5,a2,a50)") ' Got here ',llen,'  ',line1
      WRITE(20,"(a4,a"//frmt//")") '#Top',line1(8:llen)
      DO iit=1,9
        READ(15,"(a1024)") line1
c
        DO ji=1,256
          IF(line1(ji:ji+6).eq."Bottom,") EXIT
        ENDDO
        READ(line1(ji+7:ji+50),*) iimn,iimx,jjmn,jjmx
        mintop=1000000
        DO itp=iimn,iimx
          DO jtp=jjmn,jjmx
            IF(tops(itp,jtp).lt.mintop) mintop=tops(itp,jtp)
          ENDDO
        ENDDO
c
        llen=len(trim(line1))-5
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//",2(i4,a1))")
     >    line1(1:llen),mintop,',',mintop,','
      ENDDO
      GOTO 970
c
 1000 WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)")
c
c --- Get number of sources
c
      OPEN(16,FILE=infile6,STATUS='OLD'
     >  ,IOSTAT=IST)
c
 1010 READ(16,"(a1024)",END=9981) line1
      DO ii=1,500
        IF(line1(ii:ii+11).eq.'~Source Card') GOTO 1020
      ENDDO
      GOTO 1010
c
 1020 READ(16,"(a1024)",END=9981) line1
      IF(line1(1:1).eq.'#') GOTO 1020
      READ(line1,*) numsrc
      WRITE(*,*) numsrc,' radionuclide sources'
      REWIND(16)
c
      IF(ibuff.eq.1) THEN
        OPEN(17,FILE=infile7,STATUS='OLD'
     >    ,IOSTAT=IST)
c
 1030   READ(17,"(a1024)",END=9981) line1
        DO ii=1,500
          IF(line1(ii:ii+11).eq.'~Source Card') GOTO 1040
        ENDDO
        GOTO 1030
c
 1040   READ(17,"(a1024)",END=9981) line1
        IF(line1(1:1).eq.'#') GOTO 1040
        READ(line1,*) numbuf
        WRITE(*,*) numbuf,' aqueous-only sources'
        REWIND(17)
        numsrc=numsrc+numbuf
      ENDIF
c
c --- Add radionuclide sources
c
 1050 READ(16,"(a1024)",END=1060) line1
      DO ii=1,500
        IF(line1(ii:ii+11).eq.'~Source Card') THEN
          WRITE(20,"(a)") '~Source Card'
          WRITE(20,"(2a)") '#---------------------------------------',
     >      '---------------------------'
          WRITE(20,"(i5,a1)") numsrc,','
          READ(16,"(a1024)") line1
          READ(16,"(a1024)") line1
          GOTO 1050
        ENDIF
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 1050
c
c --- Add aqueous-only sources
c
 1060 IF(ibuff.eq.1) THEN
        WRITE(20,"(a28)") '# Begin aqueous-only sources'
 1070   READ(17,"(a1024)",END=9999) line1
        DO ii=1,500
          IF(line1(ii:ii+11).eq.'~Source Card') THEN
            READ(17,"(a1024)",END=9999) line1
            READ(17,"(a1024)",END=9999) line1
            llen=len(trim(line1))
            WRITE(frmt,"(i5)") llen+1
            WRITE(20,"(a1,a"//frmt//")") '#',line1
            GOTO 1070
          ENDIF
        ENDDO
        llen=len(trim(line1))
        IF(llen.eq.0) THEN
          WRITE(20,"(a)")
        Else
          WRITE(frmt,"(i5)") llen
          WRITE(20,"(a"//frmt//")") line1
        ENDIF
        GOTO 1070
      ENDIF
c
      GOTO 9999
c
 9981 WRITE(*,*) ' Number of sources not found'
      GOTO 9999
c
 9991 WRITE(*,*) ' Simulation Title Card not found'
      GOTO 9999
c
 9992 WRITE(*,*) ' Steady-state comment not found'
      GOTO 9999
c
 9993 WRITE(*,*) ' Solution Control Card'
      GOTO 9999
c
 9994 WRITE(*,*) ' Grid Card not found'
      GOTO 9999
c
 9995 WRITE(*,*) ' Initial Conditions Card not found'
      GOTO 9999
c
 9996 WRITE(*,*) ' Boundary Conditions Card not found'
      GOTO 9999
c
 9997 WRITE(*,*) ' RET all comments'
      GOTO 9999
c
 9999 CONTINUE
      STOP
      END