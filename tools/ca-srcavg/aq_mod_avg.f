c       ************************ PROGRAM aq_mod_avg ************************
c          Read src card input from ca-src2stomp and average aqueous rate
c          for selected sites/years.
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      DIMENSION modyr(25,4),ncomma(10)
      DIMENSION rateyr(13000)
      CHARACTER modin*256,modout*256,modlst*256,frmt*10
      CHARACTER line*256,sitetmp*25,site(25)*25
      CHARACTER srcfile*256,chngfile*256,strin*3,strot*3,dum1*1,dum2*1
      CHARACTER(len=256), DIMENSION(:), allocatable :: args
c
      srcfile=""
      chngfile=""
c
c --- Read command line arguments
c
      num_args = command_argument_count()
      ALLOCATE(args(num_args))
      args=""
      DO ix = 1, num_args
        CALL get_command_argument(ix,args(ix))
      ENDDO
c
c --- Read source card file name
c
      DO ich=1,256
        IF(args(1)(ich:ich).eq." ") EXIT
      ENDDO
      srcfile=args(1)(1:ich-1)
      WRITE(*,*) ' Source File = ',srcfile
c
c --- Read source averaging file name
c
      DO ich2=1,256
        IF(args(2)(ich2:ich2).eq." ") EXIT
      ENDDO
      chngfile=args(2)(1:ich2-1)
      WRITE(*,*) ' Source/Year Averaging File = ',chngfile
c
c --- read sources/years to average (limited to 25)
c
      OPEN(11,FILE=chngfile,STATUS='OLD'
     >  ,IOSTAT=IST)
      nmod=1
      READ(11,*)
  100 READ(11,"(a25,4i15)",END=110) site(nmod),modyr(nmod,1),
     >  modyr(nmod,2),modyr(nmod,3),modyr(nmod,4)
      WRITE(*,"(i5,5x,a25,4i10)") nmod,site(nmod),modyr(nmod,1),
     >  modyr(nmod,2),modyr(nmod,3),modyr(nmod,4)
      nmod=nmod+1
      IF(nmod.gt.25) THEN
        WRITE(*,*) ' Too many (>25) mods: ',nmod
        GOTO 9999
      ENDIF
      GOTO 100
c
  110 nmod=nmod-1
      CLOSE(11)
      WRITE(*,*) ' Read ',nmod,' averages.'
      WRITE(*,*)
c
c --- Start source file loop
c
      DO inc=1,nmod
        WRITE(strin,"(i3)") inc-1
        WRITE(strot,"(i3)") inc
        IF(inc.eq.1) THEN
          modin=srcfile
        ELSE
          modin=srcfile(1:ich-6)//"_srcavg"//TRIM(ADJUSTL(strin))//
     >      ".card"
        ENDIF
        modout=srcfile(1:ich-6)//"_srcavg"//TRIM(ADJUSTL(strot))//
     >    ".card"
c
        OPEN(10,FILE=modin,STATUS='OLD'
     >    ,IOSTAT=IST)
        OPEN(20,FILE=modout,
     >    STATUS='REPLACE',IOSTAT=IST)
        WRITE(*,"(a10,i5,a6,a100,a7,a100)") ' Average: ',inc,'  In: ',
     >    modin,'  Out: ',modout
c
c --- Read card file(s).
c
  200   READ(10,"(a256)",END=600) line
        DO ic=1,200
          IF(line(ic:ic+8).eq."# Site = ") GOTO 300
        ENDDO
        llen=LEN(TRIM(line))
        WRITE(frmt,"(i3)") llen
        WRITE(20,"(a"//frmt//")") line
        GOTO 200
c
  300   llen=LEN(TRIM(line))
        WRITE(frmt,"(i3)") llen
        WRITE(20,"(a"//frmt//")") line
        READ(line(ic+9:256),"(a25)") sitetmp
        IF(sitetmp.ne.site(inc)) GOTO 200
        WRITE(*,"(a10,i5,a8,a25)") ' Average: ',inc,'  Site: ',sitetmp
c
  310   READ(10,"(a256)",END=600) line
        DO ic=1,200
          IF(line(ic:ic+18).eq."Aqueous Volumetric,") GOTO 400
          IF(line(ic:ic+8).eq."# Site = ") THEN
            BACKSPACE(10)
            GOTO 200
          ENDIF
        ENDDO
        llen=LEN(TRIM(line))
        WRITE(frmt,"(i3)") llen
        WRITE(20,"(a"//frmt//")") line
        GOTO 310
c
  400   nc=1
        DO ic=1,200
          IF(line(ic:ic).eq.",") THEN
            ncomma(nc)=ic
            nc=nc+1
          ENDIF
        ENDDO
        READ(line(ncomma(1)+1:ncomma(2)-1),*) imin
        READ(line(ncomma(2)+1:ncomma(3)-1),*) imax
        READ(line(ncomma(3)+1:ncomma(4)-1),*) jmin
        READ(line(ncomma(4)+1:ncomma(5)-1),*) jmax
        READ(line(ncomma(5)+1:ncomma(6)-1),*) kmin
        READ(line(ncomma(6)+1:ncomma(7)-1),*) kmax
        READ(line(ncomma(7)+1:ncomma(8)-1),*) nlines
c
        IF(nlines.gt.13000) THEN
          WRITE(*,*) ' Too many yearly rate lines ',nlines
          GOTO 9999
        ENDIF
        rateyr=0.0
c
        READ(10,*) iyr1,dum1,rate1
        minyr=iyr1
        DO iyy=1,nlines-1
          READ(10,*) iyr2,dum2,rate2
          dfvl=rate2-rate1
          IF(iyr2.gt.iyr1) THEN
            DO jyr=iyr1,iyr2-1
              frvl=((FLOAT(jyr)+0.5)-FLOAT(iyr1))/
     >          (FLOAT(iyr2)-FLOAT(iyr1))
              rateyr(jyr)=rate1+frvl*dfvl
            ENDDO
          ENDIF
          iyr1=iyr2
          rate1=rate2
        ENDDO
        maxyr=iyr2
c
        IF((modyr(inc,1).lt.minyr).or.
     >     (modyr(inc,2).gt.maxyr)) THEN
          WRITE(*,*) ' Input year range outside list of years '
          GOTO 9999
        ENDIF
c
        IF((modyr(inc,1).lt.modyr(inc,3)).or.
     >     (modyr(inc,2).gt.modyr(inc,4))) THEN
          WRITE(*,*) ' Input year range exceeds averaged year range ',
     >      modyr(inc,1),modyr(inc,2),modyr(inc,3),modyr(inc,4)
          GOTO 9999
        ENDIF
c
        DO myr=modyr(inc,3),modyr(inc,4)
          IF((myr.lt.modyr(inc,1)).and.(rateyr(myr).gt.1e-20)) THEN
            WRITE(*,*)
     >        ' Attempting to overwrite rate outside averaging zone: ',
     >        modyr(inc,1),modyr(inc,2),myr,rateyr(myr)
            GOTO 9999
          ENDIF
          IF((myr.gt.modyr(inc,2)).and.(rateyr(myr).gt.1e-20)) THEN
            WRITE(*,*)
     >        ' Attempting to overwrite rate outside averaging zone: ',
     >        modyr(inc,1),modyr(inc,2),myr,rateyr(myr)
            GOTO 9999
          ENDIF
        ENDDO
c
        aqsum=0.0
        DO jyr=modyr(inc,1),modyr(inc,2)
          aqsum=aqsum+rateyr(jyr)
        ENDDO
        aqavg=aqsum/FLOAT(modyr(inc,4)-modyr(inc,3)+1)
        minoyr=MIN(minyr,modyr(inc,3))
        IF(modyr(inc,4).gt.modyr(inc,2)) THEN
          maxoyr=MAX(maxyr,modyr(inc,4)+1)
        ELSE
          maxoyr=MAX(maxyr,modyr(inc,4))
        ENDIF
        nlnout=1+(maxoyr-minoyr)*2
        WRITE(*,"(a11,2i5,a14,2i5)") ' In years: ',minyr,maxyr,
     >    '   Out years: ',minoyr,maxoyr
        WRITE(*,*)
c
        WRITE(20,"(a19,7(i4,a1))") "Aqueous Volumetric,",
     >    imin,",",imax,",",jmin,",",jmax,",",kmin,",",kmax,",",
     >    nlnout,","
        DO kyr=minoyr,maxoyr-1
          IF((kyr.ge.modyr(inc,3)).and.(kyr.le.modyr(inc,4))) THEN
            WRITE(20,"(i4,a7,e15.7,a11)") kyr,", year,",
     >        aqavg,", m^3/year,"
            WRITE(20,"(i4,a7,e15.7,a11)") kyr+1,", year,",
     >        aqavg,", m^3/year,"
          ELSE
            WRITE(20,"(i4,a7,e14.6,a11)") kyr,", year,",
     >        rateyr(kyr),", m^3/year,"
            WRITE(20,"(i4,a7,e14.6,a11)") kyr+1,", year,",
     >        rateyr(kyr),", m^3/year,"
          ENDIF
        ENDDO
        WRITE(20,"(i4,a7,e14.6,a11)") maxoyr,", year,",
     >    0,", m^3/year,"
c
        GOTO 310
c
  600   CONTINUE
      ENDDO
c
      REWIND(20)
      modlst=srcfile(1:ich-6)//"_srcavg_last.card"
      OPEN(22,FILE=modlst,
     >  STATUS='REPLACE',IOSTAT=IST)
c
      DO ii4=1,4
        READ(20,"(a256)") line
        WRITE(22,"(a256)") line
      ENDDO
c
  700 READ(20,"(a256)",END=9999) line
      llen=LEN(TRIM(line))
      WRITE(frmt,"(i3)") llen
      WRITE(22,"(a"//frmt//")") line
      GOTO 700
c
 9999 CONTINUE
      STOP
      END
