c       ************************ PROGRAM xprt_RTD_input_gen.f ****************************
c          Reads 1943-2018 input file and modifies for the Rad mass balance simulation.
c
c          Command line variables:
c             1) 1943-2018 input file path/name
c             2) Mass Balance Output Control Card file path/name
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
	  INTEGER plottimes(500)
      CHARACTER infile1*256,infile2*256,outfile1*80
      CHARACTER line1*1024
      CHARACTER frmt*10,frmt2*10
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
      WRITE(*,*) ' 1943-2018 input file is: ',infile1
c
c --- Read Mass Balance Output Control Card file path/name from the command line arguments
c
      READ(args(2),"(a256)") infile2
      WRITE(*,*) ' Mass Balance Output Control Card file is: ',infile2
c
      nyrend=12070
c
      irad=1
      DO ii=1,70
        IF(infile1(ii:ii+5).eq.'XPRT-2') irad=2
      ENDDO
      WRITE(*,"(a20,i1)") ' Radionuclide Group ',irad
c
      IF(irad.eq.1) THEN
        outfile1="input_XPRT-MB1"
      ELSE
        outfile1="input_XPRT-MB2"
      ENDIF
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- Read 2018 input file and revise for mass balance input
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
  100 READ(11,"(a1024)",END=9991) line1
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
  200 IF(irad.eq.1) THEN
        WRITE(20,"(a29,a1,i4,a1,i5,a2)") 
     >    'Rad1 Mass Balance Simulation ',
     >    '(',1943,'-',nyrend,'),'
      ELSE
        WRITE(20,"(a29,a1,i4,a1,i5,a2)") 
     >    'Rad2 Mass Balance Simulation ',
     >    '(',1943,'-',nyrend,'),'
      ENDIF
c
  210 READ(11,"(a1024)",END=9992) line1
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
      READ(11,*)
      READ(11,*)
      READ(11,*)
      READ(11,*) nscl
c
      WRITE(20,"(a)") 'Restart File, ../ss/restart,'
      WRITE(20,"(a)") 'Water w/ Patankar Vadose Transport Courant,1.0,'
      IF(nscl.eq.1) THEN
        WRITE(20,"(a)") '2,'
        WRITE(20,"(i4,a6,i4,a43)") 1943,',year,',
     >    2070,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
        WRITE(20,"(i4,a6,i5,a44)") 2070,',year,',
     >    nyrend,',year,1.0E-08,year,10.0,year,1.25,16,1.0E-6,'
      ELSEIF(nscl.eq.2) THEN
        READ(11,*)
        READ(11,*) inityr
        WRITE(20,"(a)") '4,'
        WRITE(20,"(i4,a6,i4,a43)") 1943,',year,',
     >    inityr,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
        WRITE(20,"(i4,a6,i4,a44)") inityr,',year,',
     >    2018,',year,1.0E-08,year,0.01,year,1.25,16,1.0E-6,'
        WRITE(20,"(i4,a6,i4,a43)") 2018,',year,',
     >    2070,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
        WRITE(20,"(i4,a6,i5,a44)") 2070,',year,',
     >    nyrend,',year,1.0E-08,year,10.0,year,1.25,16,1.0E-6,'
      ELSEIF(nscl.eq.3) THEN
        READ(11,*)
        READ(11,*) inityr,frmt,lastaq
        WRITE(20,"(a)") '4,'
        WRITE(20,"(i4,a6,i4,a43)") 1943,',year,',
     >    inityr,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
        WRITE(20,"(i4,a6,i4,a44)") inityr,',year,',
     >    lastaq,',year,1.0E-08,year,0.01,year,1.25,16,1.0E-6,'
        WRITE(20,"(i4,a6,i4,a43)") lastaq,',year,',
     >    2070,',year,1.0E-08,year,0.1,year,1.25,16,1.0E-6,'
        WRITE(20,"(i4,a6,i5,a44)") 2070,',year,',
     >    nyrend,',year,1.0E-08,year,10.0,year,1.25,16,1.0E-6,'
      ELSE
        WRITE(*,*) ' Invalid number of time periods = ',nscl
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
  310 READ(11,"(a1024)",END=9993) line1
      DO ii=1,1024
        IF(line1(ii:ii+19).eq.'~Grid Card') GOTO 400
      ENDDO
      GOTO 310
c
  400 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
c
  410 READ(11,"(a1024)",END=9994) line1
      DO ii=1,1024
        IF(line1(ii:ii+29).eq.'~Solute/Fluid Interaction Card') GOTO 500
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
  510 READ(11,"(a1024)",END=9995) line1
      DO ii=1,1024
        IF(line1(ii:ii+11).eq.'Conventional') GOTO 600
        IF(line1(ii:ii+24).eq.'# Output Control Card for') GOTO 700
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
  600 ipos1=0
      ipos2=0
      DO ii=1,1024
        IF(line1(ii:ii+10).eq.'continuous,') ipos1=ii
        IF(line1(ii:ii+4).eq.', yr,') ipos2=ii
      ENDDO
      IF((ipos1.eq.0).or.(ipos2.eq.0)) GOTO 9996
      llen=len(trim(line1))
      WRITE(frmt,"(i3)") ipos1+10
      WRITE(frmt2,"(i3)") llen-ipos2+1	  
      WRITE(20,"(a"//frmt//",a10,a"//frmt2//")")
     >  line1(1:ipos1+10),' 1.000E+20',line1(ipos2:llen)
      GOTO 510
c
  700 OPEN(12,FILE=infile2,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      READ(12,*)
      READ(12,*)
  710 READ(12,"(a1024)",END=800) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 710
c
  800 WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
  810 READ(11,"(a1024)",END=9997) line1
      DO ii=1,1024
        IF(line1(ii:ii+17).eq.'~Surface Flux Card') GOTO 900
      ENDDO
      GOTO 810
c
  900 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
      WRITE(20,"(a)") 
     >  '#---------------------------------------------------------'
      WRITE(20,"(i1,a1)") 9,','
      WRITE(20,"(a)") '#Mass Balance Information'
      READ(11,"(a1024)",END=9998) line1
      READ(11,"(a1024)",END=9998) line1
      READ(11,"(a1024)",END=9998) line1
      DO isf=1,18
        READ(11,"(a1024)",END=9998) line1
        llen=len(trim(line1))
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDDO
c
  910 READ(11,"(a1024)",END=9998) line1
      DO ii=1,1024
        IF(line1(ii:ii+9).eq.'#---------') GOTO 920
      ENDDO
      GOTO 910
c
  920 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
  930 READ(11,"(a1024)",END=9999) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 930
c
 9991 WRITE(*,*) ' 2018 comment not found'
      GOTO 9999
c
 9992 WRITE(*,*) ' Solution Control Card'
      GOTO 9999
c
 9993 WRITE(*,*) ' Grid Card not found'
      GOTO 9999
c
 9994 WRITE(*,*) ' Solute/Fluid Interaction Card not found'
      GOTO 9999
c
 9995 WRITE(*,*) 'Output Control Card not found'
      GOTO 9999
c
 9996 WRITE(*,*) ' Problem with Solute/Fluid Interaction Card'
      GOTO 9999
c
 9997 WRITE(*,*) ' Surface Flux Card not found'
      GOTO 9999
c
 9998 WRITE(*,*) ' Problem finding end of Surface Flux Card'
      GOTO 9999
c
 9999 CONTINUE
      STOP
      END