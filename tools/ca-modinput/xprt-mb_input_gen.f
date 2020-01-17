c       ************************ PROGRAM xprt-mb1_input_gen.f ****************************
c          Reads SS input file and modifies for the Rad mass balance simulation.
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      CHARACTER infile1*80,infile2*80,infile4*80
      CHARACTER infile5*80,infile6*80,infile7*80,outfile1*80
      CHARACTER line1*1024,dum1*10,dum2*10
      CHARACTER frmt*10,bcn*10,zonelist(25)*25,buff*4
      CHARACTER(len=80), DIMENSION(:), allocatable :: args
c
      irad=0
      izone=0
      nzone=0
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
c --- Read rad group from the command line arguments
c
      READ(args(1),*) irad
      WRITE(*,*) ' Rad group = ',irad
c
c --- Read buffer switch from the command line arguments
c
      IF(num_args.gt.1) THEN
        ibuff=1
        WRITE(*,*) ' Aqueous-only buffer will be read'
      ELSE
        ibuff=0
        WRITE(*,*) ' Aqueous-only buffer will not be read'
      ENDIF
c
      infile1="../ss/input_SS"
      infile2="../ret/ca_tr_boundary_card.dat"
      infile7="../sources/buffer-aq-src.card"
      IF(irad.eq.1) THEN
        infile4="rad1_Mass_Balance_Output_Control.dat"
        infile5="rad1_surface_flux.txt"
        infile6="../sources/rads1-src.card"
        IF(ibuff.eq.1) THEN
          outfile1="input_XPRT-MB1_with_buffer"
        ELSE
          outfile1="input_XPRT-MB1_no_buffer"
        ENDIF
      ELSEIF(irad.eq.2) THEN
        infile4="rad2_Mass_Balance_Output_Control.dat"
        infile5="rad2_surface_flux.txt"
        infile6="../sources/rads2-src.card"
        IF(ibuff.eq.1) THEN
          outfile1="input_XPRT-MB2_with_buffer"
        ELSE
          outfile1="input_XPRT-MB2_no_buffer"
        ENDIF
      ELSE
        WRITE(*,*) ' Rad group = ',irad,' End script'
        GOTO 9999
      ENDIF
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- Find last year for rad sources
c
      OPEN(16,FILE=infile6,STATUS='OLD'
     >  ,IOSTAT=IST)
      lastyr=0
   10 READ(16,"(a1024)",END=20) line1
      DO ic=1,200
        IF(line1(ic:ic+5).eq."Solute") THEN
          READ(line1(ise+1:256),*) dum1,dum2,i1,i2,j1,j2,k1,k2,ny
          DO iy=1,ny
            READ(16,*) iyr
            IF(iyr.gt.lastyr) lastyr=iyr
          ENDDO
        ENDIF
      ENDDO
c
      GOTO 10
c
   20 CLOSE(16)
      WRITE(*,*) ' Last year = ',lastyr
c
c --- Read SS input file and revise for rad MB input
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
  100 READ(11,"(a1024)",END=9991) line1
      DO ii=1,1024
        IF(line1(ii:ii+21).eq.'~Simulation Title Card') GOTO 200
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 100
c
  200 llen=len(trim(line1))
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
  300 IF(irad.eq.1) THEN
        WRITE(20,"(a35,i4,a2)") 'Rad1 Mass Balance Simulation (1943-',
     >    lastyr+1,'),'
      ELSE
        WRITE(20,"(a35,i4,a2)") 'Rad2 Mass Balance Simulation (1943-',
     >    lastyr+1,'),'
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
      WRITE(20,"(a)") '1,'
      WRITE(20,"(a10,i4,a43)") '1943,year,',
     >  lastyr+1,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
      WRITE(20,"(a)") '100000,'
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
      WRITE(20,"(a)") '8,'
      IF(irad.eq.1) THEN
        WRITE(20,"(2a)") '  C-14, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' Cl-36, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") '   H-3, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' I-129, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") 'Np-237, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") 'Re-187, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' Sr-90, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' Tc-99, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(a)") '0,'
      ELSE
        WRITE(20,"(2a)") ' U-232, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' U-233, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' U-234, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' U-235, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' U-236, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") ' U-238, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") 'Th-230, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
        WRITE(20,"(2a)") 'Ra-226, Conventional, 2.50e-9, m^2/s,con',
     >    'tinuous, 1.0E+20,yr, 1.0E-12, Ci/m^3,'
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
      IF(irad.eq.1) THEN
        DO izn=1,nzone
          llen=len(trim(zonelist(izn)))
          WRITE(frmt,"(i5)") llen
          WRITE(20,"(a"//frmt//",a18)") zonelist(izn),
     >      ', 0.1, m, 0.05, m,'
          WRITE(20,"(a25)") '   C-14,  0.0, mL/g, 1.0,'
          WRITE(20,"(a25)") '  Cl-36,  0.0, mL/g, 1.0,'
          WRITE(20,"(a25)") '    H-3,  0.0, mL/g, 1.0,'
          WRITE(20,"(a25)") '  I-129,  0.2, mL/g, 1.0,'
          WRITE(20,"(a25)") ' Np-237, 10.0, mL/g, 1.0,'
          WRITE(20,"(a25)") ' Re-187, 14.0, mL/g, 1.0,'
          WRITE(20,"(a25)") '  Sr-90, 22.0, mL/g, 1.0,'
          WRITE(20,"(a25)") '  Tc-99,  0.0, mL/g, 1.0,'
        ENDDO
      ELSE
        DO izn=1,nzone
          llen=len(trim(zonelist(izn)))
          WRITE(frmt,"(i5)") llen
          WRITE(20,"(a"//frmt//",a18)") zonelist(izn),
     >      ', 0.1, m, 0.05, m,'
          WRITE(20,"(a27)") '  U-232,    0.8, mL/g, 1.0,'
          WRITE(20,"(a27)") '  U-233,    0.8, mL/g, 1.0,'
          WRITE(20,"(a27)") '  U-234,    0.8, mL/g, 1.0,'
          WRITE(20,"(a27)") '  U-235,    0.8, mL/g, 1.0,'
          WRITE(20,"(a27)") '  U-236,    0.8, mL/g, 1.0,'
          WRITE(20,"(a27)") '  U-238,    0.8, mL/g, 1.0,'
          WRITE(20,"(a27)") ' Th-230, 1000.0, mL/g, 1.0,'
          WRITE(20,"(a27)") ' Ra-226,  500.0, mL/g, 1.0,'
        ENDDO
      ENDIF
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
c --- Replace SS output control with rad MB output control
c
      OPEN(14,FILE=infile4,STATUS='OLD'
     >  ,IOSTAT=IST)
  810 READ(14,"(a1024)",END=900) line1
      IF(line1(1:12).eq.'22222, year,') THEN
        IF(lastyr+1.le.9999) THEN
          WRITE(20,"(i4,a7)") lastyr+1,', year,'
        ELSE
          WRITE(20,"(i5,a7)") lastyr+1,', year,'
        ENDIF
        GOTO 810
      ENDIF
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
c --- Replace SS surface flux with rad MB surface flux
c
      OPEN(15,FILE=infile5,STATUS='OLD'
     >  ,IOSTAT=IST)
      numsrftot=0
  910 READ(15,"(a1024)",END=9982) line1
      IF((line1(1:1).eq.'#').or.(line1(1:1).eq.'~')) GOTO 910
      READ(line1,*) numsrf
      DO nsf=1,numsrf
        READ(15,"(a1024)") line1
        DO ii=1,500
          IF(line1(ii:ii+10).eq.'srf/modflow') GOTO 920
        ENDDO
        READ(line1,*) numgrp
        numsrftot=numsrftot+numgrp
        DO nsfgrp=1,numgrp
          READ(15,*)
        ENDDO
      ENDDO
      GOTO 910
c
  920 REWIND(15)
      READ(15,*)
  930 READ(15,"(a1024)",END=9982) line1
      IF((line1(1:1).eq.'#').or.(line1(1:1).eq.'~')) THEN
        llen=len(trim(line1))
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
        GOTO 930
      ENDIF
      WRITE(20,"(i5,a1)") numsrftot,','
  940 READ(15,"(a1024)",END=9982) line1
      DO ii=1,500
        IF(line1(ii:ii+10).eq.'srf/modflow') GOTO 1000
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 940
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
 9982 WRITE(*,*) ' MODFLOW flux input not found'
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
 9998 WRITE(*,*) ' Bottom not found'
      GOTO 9999
c
 9999 CONTINUE
      STOP
      END
