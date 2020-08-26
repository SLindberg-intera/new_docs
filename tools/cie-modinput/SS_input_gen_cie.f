c       ************************ PROGRAM SS_input_gen_cie.f ****************************
c          Reads input file exported from CAST, replaces recharge BC with RET SS
c          input, and replaces Output Control card.
c
c          Command line variables:
c             1) Model name
c             2) Modeler name
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      CHARACTER infile1*80,infile2*80,infile3*80,outfile1*80
      CHARACTER line1*1024,frmt*10,bcn*10
      CHARACTER date*8,time*10,model*25,modeler*25
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
c --- Read model name from the command line arguments
c
      READ(args(1),"(a25)") model
c
c --- Read modeler name from the command line arguments
c
      READ(args(2),"(a25)") modeler
c
      infile1="../build/input"
      infile2="../ret/cie_ss_boundary_card.dat"
      infile3="SS_Output_Control.dat"
      outfile1="input_cie_SS"
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
   10 READ(11,"(a1024)",END=9987) line1
      DO ii=1,1024
        IF(line1(ii:ii+21).eq.'~Simulation Title Card') GOTO 20
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 10
c
   20 WRITE(20,"(a)") '~Simulation Title Card'
      WRITE(20,"(2a)") '#------------------------',
     >  '------------------------------------------'
      WRITE(20,"(i1,a1)") 1,','
      WRITE(20,"(a)") 'Cumulative Impact Evaluation (CIE),'
c
      llen=len(trim(modeler))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//",a1)") modeler,','
      WRITE(20,"(a)") 'INTERA,'
c
      CALL DATE_AND_TIME (date,time)
c
      WRITE(20,"(6a)") date(5:6),'/',
     >  date(7:8),'/',date(1:4),','
c
      WRITE(20,"(6a)") time(1:2),':',
     >  time(3:4),':',time(5:6),','
c
      WRITE(20,"(i1,a1)") 2,','
      llen=len(trim(model))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//",a1)") model,','
      WRITE(20,"(a)") 'Steady-state simulation,'
c
      WRITE(20,"(2a)") '#------------------------',
     >  '------------------------------------------'
      WRITE(20,"(a)") ''
      WRITE(20,"(2a)") '#------------------------',
     >  '------------------------------------------'
c
   30 READ(11,"(a1024)",END=9988) line1
      DO ii=1,1024
        IF(line1(ii:ii+16).eq.'# Note: For dates') GOTO 40
      ENDDO
      GOTO 30
c
   40 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
c
   50 READ(11,"(a1024)",END=9989) line1
c
      DO ii=1,1024
        IF(line1(ii:ii+36).eq.'~Y-Aqueous Relative Permeability Card')
     >    WRITE(20,"(/,2a)") '#------------------------',
     >      '------------------------------------------'
        IF(line1(ii:ii+36).eq.'~Z-Aqueous Relative Permeability Card')
     >    WRITE(20,"(/,2a)") '#------------------------',
     >      '------------------------------------------'
      ENDDO
c
      DO ii=1,1024
        IF(line1(ii:ii+29).eq.'~Solute/Fluid Interaction Card') GOTO 60
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 50
c
   60 READ(11,"(a1024)",END=9990) line1
      DO ii=1,1024
        IF(line1(ii:ii+23).eq.'~Initial Conditions Card') GOTO 70
      ENDDO
      GOTO 60
c
   70 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
c
  100 READ(11,"(a1024)",END=9991) line1
      DO ii=1,1024
        IF(line1(ii:ii+24).eq.'~Boundary Conditions Card') GOTO 200
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
  200 OPEN(12,FILE=infile2,STATUS='OLD'
     >  ,IOSTAT=IST)
      llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
      WRITE(20,"(2a)") '#------------------------',
     >  '------------------------------------------'
  210 READ(12,"(a1024)",END=9992) line1
      IF(line1(1:1).ne.'#') GOTO 220
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 210
c
  220 READ(line1,*) nbc
      WRITE(bcn,"(i5)") nbc+1
      llen=len(trim(ADJUSTL(bcn)))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//",a1)") ADJUSTL(bcn),','
  230 READ(12,"(a1024)",END=300) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 230
c
  300 WRITE(20,"(a)") 'file, input.bot, Dirichlet Aqueous,'
      WRITE(20,"(a)") '1,'
      WRITE(20,"(a)") '0, year, 101325, Pa,'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
  310 READ(11,"(a1024)",END=9993) line1
      DO ii=1,1024
        IF(line1(ii:ii+11).eq.'~Source Card') GOTO 400
      ENDDO
      GOTO 310
c
  400 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
  410 READ(11,"(a1024)",END=9993) line1
      DO ii=1,1024
        IF(line1(ii:ii+19).eq.'~Output Control Card') GOTO 500
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
  500 OPEN(13,FILE=infile3,STATUS='OLD'
     >  ,IOSTAT=IST)
      READ(13,"(a1024)") line1
  510 READ(13,"(a1024)",END=600) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 510
c
  600 WRITE(20,"(a)")
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
  610 READ(11,"(a1024)",END=9994) line1
      DO ii=1,1024
        IF(line1(ii:ii+17).eq.'~Surface Flux Card') GOTO 700
      ENDDO
      GOTO 610
c
  700 llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
  710 READ(11,"(a1024)",END=9999) line1
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 710
c
      GOTO 9999
c
 9987 WRITE(*,*) ' Simulation Title Card not found'
      GOTO 9999
c
 9988 WRITE(*,*) ' # Note: For dates... not found'
      GOTO 9999
c
 9989 WRITE(*,*) ' Solute/Fluid Interaction Card not found'
      GOTO 9999
c
 9990 WRITE(*,*) ' Initial Conditions Card not found'
      GOTO 9999
c
 9991 WRITE(*,*) ' Boundary Conditions Card not found'
      GOTO 9999
c
 9992 WRITE(*,*) ' RET input all comments'
      GOTO 9999
c
 9993 WRITE(*,*) ' Bottom not found'
      GOTO 9999
c
 9994 WRITE(*,*) ' Surface Flux Card not ended'
      GOTO 9999
c
 9995 WRITE(*,*) ' Did not find node'
      GOTO 9999
c
 9996 WRITE(*,*) ' Reference Node Variables not found'
      GOTO 9999
c
 9997 WRITE(*,*) ' Reference Node Variables not ended'
      GOTO 9999
c
 9999 CONTINUE
      STOP
      END
