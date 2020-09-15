c       ************************ PROGRAM xprt_RTD_input_gen_cie.f ****************************
c          Reads 1943 - 2018 input file and modifies for the 2018 - RTD year simulation.
c
c          Command line variables:
c             1) 1943-2018 input file path/name
c             2) Simulation RTD Year
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
	  INTEGER plottimes(500)
      CHARACTER infile1*256,outfile1*80
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
c --- Read simulation RTD year from the command line arguments
c
      READ(args(2),*) nyrrtd
      WRITE(*,*) ' Simulation RTD Year = ',nyrrtd
      WRITE(*,*)
c
      nyrend=nyrrtd
c
      outfile1="input_XPRT_RTD"
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- Read 2018 input file and revise for RTD input
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
  200 WRITE(20,"(a25,a1,i4,a1,i4,a13)") 
     >    'CIE Transport Simulation ',
     >    '(',2018,'-',nyrend,' [RTD Year]),'
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
      WRITE(20,"(a26,a9)") 'Restart File, ../xprt-2018',
     >    '/restart,'
c
      WRITE(20,"(a)") 'Water w/ Patankar Vadose Transport Courant,1.0,'
      WRITE(20,"(a)") '1,'
c
      WRITE(20,"(i4,a6,i4,a43)") 2018,',year,',
     >  nyrrtd,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
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
        IF(line1(ii:ii+21).eq.'ZNC Aqueous Volumetric') GOTO 500
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
  500 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
c
      READ(11,*) nplttim
c
      iocyrfnd=0
      inpl=0
      DO ipt=1,nplttim
        READ(11,*) plottimes(ipt)
        IF(ABS(plottimes(ipt)-2018.0).lt.1.0E-10) iocyrfnd=1
        IF(((plottimes(ipt)-2018.0).gt.-1.0E-10).and.(inpl.eq.0))
     >    inpl=ipt
      ENDDO
c
      IF(iocyrfnd.ne.1) nplttim=nplttim+1
      WRITE(20,"(i3,a1)") nplttim,','
c
      IF(inpl.eq.0) THEN
        WRITE(*,*) ' STOP: No times gt 2018'
        GOTO 9999
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
        WRITE(20,"(f13.8,a7)") 2018+0.00000001_8,', year,'
c
        IF(iocyrfnd.eq.1) THEN
          inpl=inpl+1
          nplttim=nplttim+1
        ENDIF
c
        DO iocyr=inpl,nplttim-1
          IF(plottimes(iocyr).gt.9999) THEN
            WRITE(frmt,"(i5)") 5
          ELSE
            WRITE(frmt,"(i5)") 4
          ENDIF
          WRITE(20,"(i"//frmt//",a7)") plottimes(iocyr),', year,'
        ENDDO
      ENDIF
c
  510 READ(11,"(a1024)",END=9999) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 510
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
 9999 CONTINUE
      STOP
      END