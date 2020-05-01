c       ************************ PROGRAM xprt_12070_input_gen.f ****************************
c          Reads 1943 - 2018 input file and modifies for the Rad 2018 (or RTD year) - 12070 simulation.
c
c          Command line variables:
c             1) 1943-2018 input file path/name
c             2) Simulation start year (2018 if no RTD; RTD year if RTD included)
c             3) Source zone RTD IC file path/name (included only if the model has RTD [start year > 2018])
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
	  INTEGER plottimes(500)
      CHARACTER infile1*256,infile2*256,outfile1*80
      CHARACTER line1*1024
      CHARACTER frmt*10
      CHARACTER(len=256), DIMENSION(:), allocatable :: args
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
c --- Read 1943-2018 input file path/name from the command line arguments
c
      READ(args(1),"(a256)") infile1
      WRITE(*,*) ' 1943-2018 input file is = ',infile1
c
      irad=1
      DO ii=1,240
        IF(infile1(ii:ii+5).eq.'XPRT-2') irad=2
      ENDDO
      WRITE(*,"(a20,i1)") ' Radionuclide Group ',irad
c
c --- Read simulation start year from the command line arguments
c
      READ(args(2),*) nyrstrt
      WRITE(*,*) ' Simulation Start Year = ',nyrstrt
      WRITE(*,*)
c
c --- If start year > 2018, read RTD IC input file(s) path/name from the command line arguments
c
      IF(nyrstrt.gt.2018) THEN
        READ(args(3),"(a256)") infile2
        WRITE(*,*) ' Source zone RTD IC input file is = ',infile2
      ELSE
        WRITE(*,*) ' No RTD for this model'
      ENDIF
c
      nyrend=12070
c
      IF(irad.eq.1) THEN
          outfile1="input_XPRT-1_12070"
      ELSE
          outfile1="input_XPRT-2_12070"
      ENDIF
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- Read 2018 input file and revise for 12070 input
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
  100 READ(11,"(a1024)",END=9992) line1
      DO ii=1,1024
        IF(line1(ii:ii+8).eq.'1943-2018') GOTO 200
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
  200 IF(nyrend.lt.10000) THEN
        WRITE(frmt,"(i5)") 4
      ELSE
        WRITE(frmt,"(i5)") 5
      ENDIF
      IF(irad.eq.1) THEN
        IF(nyrstrt.eq.2018) THEN
          WRITE(20,"(a26,a1,i4,a1,i5,a2)") 
     >      'Rad1 Transport Simulation ',
     >      '(',nyrstrt,'-',nyrend,'),'
        ELSE
          WRITE(20,"(a26,a1,i4,a14,i5,a2)") 
     >      'Rad1 Transport Simulation ',
     >      '(',nyrstrt,' [RTD Year] - ',nyrend,'),'
        ENDIF
      ELSE
        IF(nyrstrt.eq.2018) THEN
          WRITE(20,"(a26,a1,i4,a1,i5,a1)") 
     >      'Rad2 Transport Simulation ',
     >      '(',nyrstrt,'-',nyrend,')'
        ELSE
          WRITE(20,"(a26,a1,i4,a14,i5,a1)") 
     >      'Rad2 Transport Simulation ',
     >      '(',nyrstrt,' [RTD Year] - ',nyrend,')'
        ENDIF
      ENDIF
c
  210 READ(11,"(a1024)",END=9993) line1
      DO ii=1,1024
        IF(line1(ii:ii+21).eq.'~Solution Control Card') GOTO 300
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
  300 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
      IF(irad.eq.1) THEN
        IF(nyrstrt.eq.2018) THEN
          WRITE(20,"(a32)") 'Restart File, ../xprt-1/restart,'
        ELSE
          WRITE(20,"(a36)") 'Restart File, ../xprt-1-rtd/restart,'
        ENDIF
      ELSEIF(irad.eq.2) THEN
        IF(nyrstrt.eq.2018) THEN
          WRITE(20,"(a32)") 'Restart File, ../xprt-2/restart,'
        ELSE
          WRITE(20,"(a36)") 'Restart File, ../xprt-2-rtd/restart,'
        ENDIF
      ELSE
        WRITE(*,*) ' Rad group = ',irad,' End script'
        GOTO 9999
      ENDIF
c
      WRITE(20,"(a)") 'Water w/ Patankar Vadose Transport Courant,1.0,'
      WRITE(20,"(a)") '2,'
c
      WRITE(20,"(i4,a6,i4,a43)") nyrstrt,',year,',
     >  2070,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
      WRITE(20,"(i4,a6,i5,a44)") 2070,',year,',
     >  12070,',year,1.0E-08,year,10.0,year,1.25,16,1.0E-6,'
c
      WRITE(20,"(a)") '1000000,'
      WRITE(20,"(a)") '0,'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
  310 READ(11,"(a1024)",END=9994) line1
      DO ii=1,1024
        IF(line1(ii:ii+19).eq.'~Grid Card') GOTO 400
      ENDDO
      GOTO 310
c
  400 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
c
  410 READ(11,"(a1024)",END=9995) line1
      DO ii=1,1024
        IF(line1(ii:ii+22).eq.'Initial Conditions Card') GOTO 600
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 410
c
c --- Replace Initial Conditions Card
c
  600 IF(nyrstrt.gt.2018) THEN
c
c --- Read source zone RTD file and determine the number of initial conditions
c
        OPEN(30,FILE=infile2,STATUS='OLD'
     >    ,IOSTAT=IST)
c
        nrtd=0
  610   READ(30,"(a1024)",END=620) line1
        DO ii=1,1024
          IF(line1(ii:ii+8).eq.'Overwrite') nrtd=nrtd+1
        ENDDO
        GOTO 610
c
  620   CLOSE(30)
c
c --- Write the number of initial conditions
c
        WRITE(20,"(a24)") '~Initial Conditions Card'
        WRITE(20,"(2a)") '#---------------------------------------',
     >    '---------------------------'
        WRITE(20,"(a)") 'Gas Pressure, Aqueous Pressure,'
        IF(nrtd.lt.10) THEN
          WRITE(20,"(i1,a1)") nrtd,','
        ELSEIF(nrtd.lt.100) THEN
          WRITE(20,"(i2,a1)") nrtd,','
        ELSEIF(nrtd.lt.1000) THEN
          WRITE(20,"(i3,a1)") nrtd,','
        ELSE 
          WRITE(20,"(i6,a1)") nrtd,','
        ENDIF
        WRITE(20,"(2a)") '#---------------------------------------',
     >    '---------------------------'
c
c --- Replace Initial Conditions Card with RTD file(s)
c
        OPEN(30,FILE=infile2,STATUS='OLD'
     >    ,IOSTAT=IST)
c
  650   READ(30,"(a1024)",END=660) line1
        llen=len(trim(line1))
        IF(llen.eq.0) THEN
          WRITE(20,"(a)")
        ELSE
          WRITE(frmt,"(i5)") llen
          WRITE(20,"(a"//frmt//")") line1
        ENDIF
        GOTO 650
c
  660   CLOSE(30)
c
        WRITE(20,"(2a)") '#---------------------------------------',
     >    '---------------------------'
        WRITE(20,"(a)")
        WRITE(20,"(2a)") '#---------------------------------------',
     >    '---------------------------'
c
      ELSE
        WRITE(20,"(a24)") '~Initial Conditions Card'
        WRITE(20,"(2a)") '#---------------------------------------',
     >    '---------------------------'
        WRITE(20,"(a)") 'Gas Pressure, Aqueous Pressure,'
        WRITE(20,"(a)") '0,'
        WRITE(20,"(2a)") '#---------------------------------------',
     >    '---------------------------'
        WRITE(20,"(a)")
        WRITE(20,"(2a)") '#---------------------------------------',
     >    '---------------------------'
      ENDIF
c
  690 READ(11,"(a1024)",END=9996) line1
      DO ii=1,1024
        IF(line1(ii:ii+24).eq.'~Boundary Conditions Card') GOTO 700
      ENDDO
      GOTO 690
c
  700 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
c
  710 READ(11,"(a1024)",END=9995) line1
      DO ii=1,1024
        IF(line1(1:22).eq."ZNC Aqueous Volumetric") GOTO 800
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 710
c
  800 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
      READ(11,*) nplttim
      iocyrfnd=0
      inpl=0
      DO ipt=1,nplttim
        READ(11,*) plottimes(ipt)
        IF(plottimes(ipt).eq.nyrstrt) iocyrfnd=1
        IF((plottimes(ipt).ge.nyrstrt).and.(inpl.eq.0)) inpl=ipt
      ENDDO
c
      IF(iocyrfnd.ne.1) nplttim=nplttim+1
      WRITE(20,"(i3,a1)") nplttim,','
c
      IF(inpl.eq.0) THEN
        WRITE(*,*) ' No times gt ',nyrstrt
      ELSE
        DO iocyr=1,inpl-1
          IF(plottimes(iocyr).gt.9999) THEN
            WRITE(frmt,"(i5)") 5
          ELSE
            WRITE(frmt,"(i5)") 4
          ENDIF
          WRITE(20,"(i"//frmt//",a7)") plottimes(iocyr),', year,'
        ENDDO
c
        WRITE(20,"(f13.8,a7)") nyrstrt+0.00000001_8,', year,'
c
        IF(iocyrfnd.eq.1) inpl=inpl+1
        IF(iocyrfnd.eq.0) nplttim=nplttim-1
c
        DO iocyr=inpl,nplttim
          IF(plottimes(iocyr).gt.9999) THEN
            WRITE(frmt,"(i5)") 5
          ELSE
            WRITE(frmt,"(i5)") 4
          ENDIF
          WRITE(20,"(i"//frmt//",a7)") plottimes(iocyr),', year,'
        ENDDO
      ENDIF
c
  810 READ(11,"(a1024)",END=9999) line1
      DO ii=1,1024
        IF(line1(ii:ii+13).eq.'Final Restart,') line1="No Restart, ,"
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
 9992 WRITE(*,*) ' 1943-2018 comment not found'
      GOTO 9999
c
 9993 WRITE(*,*) ' Solution Control Card not found'
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
 9999 CONTINUE
      STOP
      END