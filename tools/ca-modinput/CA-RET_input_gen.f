c       ************************ PROGRAM CA-RET_input_gen.f ****************************
c          Reads SS input file, modifies the Simulation Title Card, Solution Control
c          Card, and Initial Conditions Card, and replaces RET SS input with transient
c          RET input.
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      CHARACTER infile1*80,infile2*80,outfile1*80
      CHARACTER line1*1024,frmt*10,bcn*10
      CHARACTER date*8,time*10
c
      CALL DATE_AND_TIME (date,time)
c
      infile1="../ss/input_SS"
      infile2="../ret/ca_tr_boundary_card.dat"
      outfile1="input_CA-RET"
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
      WRITE(20,"(2a)") '# CA-RET input file generated by ',
     >  'CA-RET_input_gen_olive.exe  Version 1.0 - 11-8-2019'
      WRITE(20,"(12a)") '# Run on ',date(5:6),'-',
     >  date(7:8),'-',date(1:4),' at ',time(1:2),':',
     >  time(3:4),':',time(5:6)
      WRITE(20,"(a)") '#'
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
      READ(11,*)
      READ(11,*)
      READ(11,*)
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
  300 WRITE(20,"(a)") 'CA-RET Simulation (1943-2571),'
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
      WRITE(20,"(a)") 'Water,'
      WRITE(20,"(a)") '1,'
      WRITE(20,"(a)")
     >  '1943,year,2571,year,3.1688E-08,year,0.1,year,1.25,16,1.0E-6,'
      WRITE(20,"(a)") '10000,'
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
  600 llen=len(trim(line1))
      WRITE(frmt,"(i5)") llen
      WRITE(20,"(a"//frmt//")") line1
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
  800 WRITE(20,"(a)") 'file, input.bot, Dirichlet Aqueous,'
      WRITE(20,"(a)") '1,'
      WRITE(20,"(a)") '0, year, 101325, Pa,'
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
      WRITE(20,"(a)")
      WRITE(20,"(2a)") '#---------------------------------------',
     >  '---------------------------'
c
  810 READ(11,"(a1024)",END=9993) line1
      DO ii=1,1024
        IF(line1(ii:ii+11).eq.'~Source Card') GOTO 900
      ENDDO
      GOTO 810
c
  900 llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
  910 READ(11,"(a1024)",END=9999) line1
      DO ii=1,1024
        IF(line1(ii:ii+11).eq.'10000, year,')
     >    line1(ii:ii+11) = '2571, year, '
        IF(line1(ii:ii+15).eq.'Final Restart, ,')
     >    line1(ii:ii+15) = 'No Restart, ,   '
      ENDDO
      llen=len(trim(line1))
      IF(llen.eq.0) THEN
        WRITE(20,"(a)")
      Else
        WRITE(frmt,"(i5)") llen
        WRITE(20,"(a"//frmt//")") line1
      ENDIF
      GOTO 910
c
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
