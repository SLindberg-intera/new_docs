c       ************************ PROGRAM srcloc_modify.f ****************************
c          Read src card input from Mark's script and adjust locations of
c          selected source nodes (input file - "src_node_changes.dat").
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      DIMENSION imod(50,2),jmod(50,2),ncomma(10),ktop(1000,1000)
      CHARACTER modin*25,modout*25,modlst*25,radname*25
      CHARACTER line*256,lineyr(200)*256,sitetmp*25,site(50)*25
      CHARACTER(len=80), DIMENSION(:), allocatable :: args
      CHARACTER srcfile*80,strin*3,strot*3,type(50)*6,ttmp*6
      CHARACTER date*8,time*10
c
      srcfile=""
      type=""
c
c --- Read command line arguments
c
      num_args = command_argument_count()
      IF(num_args.gt.1) ibuff=1
      ALLOCATE(args(num_args))
      args=""
      DO ix = 1, num_args
        CALL get_command_argument(ix,args(ix))
      ENDDO
c
      DO ich=1,80
        IF(args(1)(ich:ich).eq." ") EXIT
      ENDDO
      srcfile=args(1)(1:ich-1)
      WRITE(*,*) srcfile
c
      CALL DATE_AND_TIME (date,time)
c
c --- read input.top
c
      ktop=0
      OPEN(12,FILE="input.top",STATUS='OLD'
     >  ,IOSTAT=IST)
   50 READ(12,*,END=60) inod,jnod,knod
      ktop(inod,jnod)=knod
      GOTO 50
c
c --- read source node changes
c
   60 OPEN(11,FILE="src_node_changes.dat",STATUS='OLD'
     >  ,IOSTAT=IST)
      nmod=0
      READ(11,*)
  100 READ(11,*,END=110) sitetmp,istrt,jstrt,iend,jend,ttmp
      nmod=nmod+1
      IF(nmod.gt.50) THEN
        WRITE(*,*) ' Too many source moves ',nmod,' ; 50 max'
        GOTO 9999
      ENDIF
      site(nmod)=sitetmp
      imod(nmod,1)=istrt
      imod(nmod,2)=iend
      jmod(nmod,1)=jstrt
      jmod(nmod,2)=jend
      type(nmod)=ttmp
      WRITE(*,*) nmod,imod(nmod,1),imod(nmod,2),jmod(nmod,1),
     >  jmod(nmod,2),type(nmod)
      GOTO 100
c
  110 CLOSE(11)
      WRITE(*,*) ' Read ',nmod,' source nodes to move.'
c
c --- Start source file loop
c
      DO inc=1,nmod
        ifound=0
        ndef=0
        WRITE(strin,"(i3)") inc-1
        WRITE(strot,"(i3)") inc
        IF(inc.eq.1) THEN
          modin=srcfile
        ELSE
          modin=srcfile(1:ich-6)//"_mod"//TRIM(ADJUSTL(strin))//".card"
        ENDIF
        modout=srcfile(1:ich-6)//"_mod"//TRIM(ADJUSTL(strot))//".card"
c
        OPEN(10,FILE=modin,STATUS='OLD'
     >    ,IOSTAT=IST)
        OPEN(20,FILE=modout,
     >    STATUS='REPLACE',IOSTAT=IST)
        WRITE(*,*) inc,modin,modout
c
c --- Read card file(s).
c
  200   READ(10,"(a256)",END=600) line
        DO ic=1,200
          IF(line(ic:ic+18).eq."Aqueous Volumetric,") ndef=ndef+1
          IF(line(ic:ic+6).eq."Solute,") ndef=ndef+1
          IF(line(ic:ic+8).eq."# Site = ") GOTO 300
        ENDDO
        WRITE(20,"(a256)") line
        GOTO 200
c
  300   WRITE(20,"(a256)") line
        READ(line(ic+9:256),"(a25)") sitetmp
        IF(sitetmp.ne.site(inc)) GOTO 200
c
  310   READ(10,"(a256)",END=600) line
        DO ic=1,200
          IF(line(ic:ic+18).eq."Aqueous Volumetric,") ndef=ndef+1
          IF(line(ic:ic+18).eq."Aqueous Volumetric,") GOTO 400
          IF(line(ic:ic+6).eq."Solute,") ndef=ndef+1
          IF(line(ic:ic+6).eq."Solute,") GOTO 500
          IF(line(ic:ic+8).eq."# Site = ") THEN
            BACKSPACE(10)
            GOTO 200
          ENDIF
        ENDDO
        WRITE(20,"(a256)") line
        GOTO 310
c
  400   nc=1
        DO ic=1,200
          IF(line(ic:ic).eq.",") THEN
            ncomma(nc)=ic
c            WRITE(*,*) nc,ncomma(nc)
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
        IF(kmin.ne.kmax) THEN
          WRITE(*,*) ' kmin <> kmax: ',kmin,kmax
          GOTO 9999
        ENDIF
        numi=imax-imin+1
        numj=jmax-jmin+1
c
        if((imod(inc,1).lt.imin).or.(imod(inc,1).gt.imax).or.
     >     (jmod(inc,1).lt.jmin).or.(jmod(inc,1).gt.jmax)) THEN
          WRITE(20,"(a256)") line
          GOTO 310
        ENDIF
c
        ifound=1
        IF(nlines.gt.200) THEN
          WRITE(*,*) ' Too many yearly rate lines ',nlines
          GOTO 9999
        ENDIF
        DO nln=1,nlines
          READ(10,"(a256)") lineyr(nln)
        ENDDO
c
        IF(type(inc).eq."single") THEN
c
c --- Single node move
c
          WRITE(*,"(a16,a15,a6,i5,a1,i5,a4,i5,a1,i5,a10)")
     >      'Single move for ',site(inc),' from ',imod(inc,1),'/',
     >      jmod(inc,1),' to ',imod(inc,2),'/',jmod(inc,2),' - Aqueous'
c
          IF(ktop(imod(inc,2),jmod(inc,2)).lt.kmin) THEN
            knew=ktop(imod(inc,2),jmod(inc,2))
            WRITE(*,*)
            WRITE(*,"(a5,i3,a1,i3,a24,i3,a4,i3)") ' Node ',imod(inc,2),
     >        '/',jmod(inc,2),' top adjusted down from ',kmin,' to ',knew
            WRITE(*,*)
          ELSE
            knew=kmin
          ENDIF
c
          WRITE(20,"(a19,7(i4,a1))") "Aqueous Volumetric,",
     >      imod(inc,2),",",imod(inc,2),",",jmod(inc,2),",",
     >      jmod(inc,2),",",knew,",",knew,",",nlines,","
          DO nln=1,nlines
            WRITE(20,"(a256)") lineyr(nln)
          ENDDO
c
          DO iii=imin,imax
            DO jjj=jmin,jmax
              IF((imod(inc,1).eq.iii).and.(jmod(inc,1).eq.jjj)) THEN
                CYCLE
              ELSE
                WRITE(20,"(a19,7(i4,a1))") "Aqueous Volumetric,",
     >            iii,",",iii,",",jjj,",",jjj,",",kmin,",",kmax,",",
     >            nlines,","
                  ndef=ndef+1
                DO nln=1,nlines
                  WRITE(20,"(a256)") lineyr(nln)
                ENDDO
              ENDIF
            ENDDO
          ENDDO
          GOTO 310
c
c --- End single node move
c
        ELSEIF(type(inc).eq."block ") THEN
c
c --- Block move
c
          WRITE(*,"(2a15,a6,i5,a1,i5,a4,i5,a1,i5,a10)")
     >      'Block move for ',site(inc),' from ',imod(inc,1),'/',
     >      jmod(inc,1),' to ',imod(inc,2),'/',jmod(inc,2),' - Aqueous'
c
          DO ibl=imod(inc,2),imod(inc,2)+numi-1
            DO jbl=jmod(inc,2),jmod(inc,2)+numj-1
              IF(ktop(ibl,jbl).lt.kmin) THEN
                knew=ktop(ibl,jbl)
              ELSE
                knew=kmin
              ENDIF
            ENDDO
          ENDDO
          IF(knew.ne.kmin)
     >      WRITE(*,"(a5,i3,a1,i3,a24,i3,a4,i3,a10)") ' Node ',
     >        ibl,'/',jbl,
     >        ' top adjusted down from ',kmin,' to ',knew,' - Aqueous'
c
          WRITE(20,"(a19,7(i4,a1))") "Aqueous Volumetric,",
     >      imod(inc,2),",",imod(inc,2)+numi-1,",",jmod(inc,2),",",
     >      jmod(inc,2)+numj-1,",",knew,",",knew,",",nlines,","
          DO nln=1,nlines
            WRITE(20,"(a256)") lineyr(nln)
          ENDDO
c
          GOTO 310
c
c --- End block move
c
        ELSE
          WRITE(*,*) ' Invalid move type - ,',imod,type(inc)
          GOTO 9999
        ENDIF
c
  500   nc=1
        DO ic=1,200
          IF(line(ic:ic).eq.",") THEN
            ncomma(nc)=ic
c            WRITE(*,*) nc,ncomma(nc)
            nc=nc+1
          ENDIF
        ENDDO
        READ(line(ncomma(1)+1:ncomma(2)-1),*) radname
        READ(line(ncomma(2)+1:ncomma(3)-1),*) imin
        READ(line(ncomma(3)+1:ncomma(4)-1),*) imax
        READ(line(ncomma(4)+1:ncomma(5)-1),*) jmin
        READ(line(ncomma(5)+1:ncomma(6)-1),*) jmax
        READ(line(ncomma(6)+1:ncomma(7)-1),*) kmin
        READ(line(ncomma(7)+1:ncomma(8)-1),*) kmax
        READ(line(ncomma(8)+1:ncomma(9)-1),*) nlines
        IF(kmin.ne.kmax) THEN
          WRITE(*,*) ' kmin <> kmax: ',kmin,kmax
          GOTO 9999
        ENDIF
        numi=imax-imin+1
        numj=jmax-jmin+1
c
        if((imod(inc,1).lt.imin).or.(imod(inc,1).gt.imax).or.
     >     (jmod(inc,1).lt.jmin).or.(jmod(inc,1).gt.jmax)) THEN
          WRITE(20,"(a256)") line
          GOTO 310
        ENDIF
c
        IF(nlines.gt.200) THEN
          WRITE(*,*) ' Too many yearly rate lines ',nlines
          GOTO 9999
        ENDIF
        DO nln=1,nlines
          READ(10,"(a256)") lineyr(nln)
        ENDDO
c
        IF(type(inc).eq."single") THEN
c
c --- Single node move
c
          WRITE(*,"(a16,a15,a6,i5,a1,i5,a4,i5,a1,i5,a3,a6)")
     >      'Single move for ',site(inc),' from ',imod(inc,1),'/',
     >      jmod(inc,1),' to ',imod(inc,2),'/',jmod(inc,2),' - ',radname
c
          IF(ktop(imod(inc,2),jmod(inc,2)).lt.kmin) THEN
            knew=ktop(imod(inc,2),jmod(inc,2))
            WRITE(*,*)
            WRITE(*,"(a5,i3,a1,i3,a24,i3,a4,i3)") ' Node ',imod(inc,2),
     >        '/',jmod(inc,2),' top adjusted down from ',kmin,' to ',knew
            WRITE(*,*)
          ELSE
            knew=kmin
          ENDIF
c
          WRITE(20,"(a8,a6,a1,7(i4,a1))") "Solute, ",radname,",",
     >      imod(inc,2),",",imod(inc,2),",",jmod(inc,2),",",
     >      jmod(inc,2),",",kmin,",",kmax,",",nlines,","
          DO nln=1,nlines
            WRITE(20,"(a256)") lineyr(nln)
          ENDDO
c
          DO iii=imin,imax
            DO jjj=jmin,jmax
              IF((imod(inc,1).eq.iii).and.(jmod(inc,1).eq.jjj)) THEN
                CYCLE
              ELSE
                WRITE(20,"(a8,a6,a1,7(i4,a1))") "Solute, ",radname,",",
     >            iii,",",iii,",",jjj,",",jjj,",",kmin,",",kmax,",",
     >            nlines,","
                  ndef=ndef+1
                DO nln=1,nlines
                  WRITE(20,"(a256)") lineyr(nln)
                ENDDO
              ENDIF
            ENDDO
          ENDDO
          GOTO 310
c
c --- End single node move
c
        ELSEIF(type(inc).eq."block ") THEN
c
c --- Block move
c
          WRITE(*,"(2a15,a6,i5,a1,i5,a4,i5,a1,i5,a3,a6)")
     >      'Block move for ',site(inc),' from ',imod(inc,1),'/',
     >      jmod(inc,1),' to ',imod(inc,2),'/',jmod(inc,2),' - ',radname
c
          DO ibl=imod(inc,2),imod(inc,2)+numi-1
            DO jbl=jmod(inc,2),jmod(inc,2)+numj-1
              IF(ktop(ibl,jbl).lt.kmin) THEN
                knew=ktop(ibl,jbl)
              ELSE
                knew=kmin
              ENDIF
            ENDDO
          ENDDO
          IF(knew.ne.kmin)
     >      WRITE(*,"(a5,i3,a1,i3,a24,i3,a4,i3,a3,a6)") ' Node ',
     >        ibl,'/',jbl,
     >        ' top adjusted down from ',kmin,' to ',knew,' - ',radname
c
          WRITE(20,"(a8,a6,a1,7(i4,a1))") "Solute, ",radname,",",
     >      imod(inc,2),",",imod(inc,2)+numi-1,",",jmod(inc,2),",",
     >      jmod(inc,2)+numj-1,",",knew,",",knew,",",nlines,","
          DO nln=1,nlines
            WRITE(20,"(a256)") lineyr(nln)
          ENDDO
c
          GOTO 310
c
c --- End block move
c
        ELSE
          WRITE(*,*) ' Invalid move type - ,',imod,type(inc)
          GOTO 9999
        ENDIF
c
  600   CONTINUE
        IF(ifound.eq.0) GOTO 9990
c
      ENDDO
c
      REWIND(20)
      modlst=srcfile(1:ich-6)//"_mod_last.card"
      OPEN(22,FILE=modlst,
     >  STATUS='REPLACE',IOSTAT=IST)
c
      DO ii4=1,4
        READ(20,"(a256)") line
        WRITE(22,"(a256)") line
      ENDDO
c
      WRITE(22,"(a)") '#'
      WRITE(22,"(2a)") '# Source nodes moved by ',
     >  'srcloc_modify_olive.exe  Version 1.0 - 11-8-2019'
      WRITE(22,"(12a)") '# Run on ',date(5:6),'-',
     >  date(7:8),'-',date(1:4),' at ',time(1:2),':',
     >  time(3:4),':',time(5:6)
      WRITE(22,"(a)") '#'
c
  700 READ(20,"(a256)",END=9999) line
      DO ic=1,200
        IF(line(ic:ic+11).eq."~Source Card") THEN
          WRITE(22,"(a256)") line
          READ(20,"(a256)") line
          WRITE(22,"(a256)") line
          READ(20,"(a256)") line
          IF(ndef.lt.100) THEN
            WRITE(22,"(i2,a1)") ndef,','
          ELSEIF(ndef.lt.1000) THEN
            WRITE(22,"(i3,a1)") ndef,','
          ELSEIF(ndef.lt.10000) THEN
            WRITE(22,"(i4,a1)") ndef,','
          ELSE
            WRITE(22,"(i10,a1)") ndef,','
          ENDIF
          GOTO 700
        ENDIF
      ENDDO
      WRITE(22,"(a256)") line
      GOTO 700
c
      GOTO 9999
c
 9990 CONTINUE
      WRITE(20,*) ' Did not find source node ',
     >  imod(inc,1),jmod(inc,1)
      WRITE(*,*) ' Did not find source node ',
     >  imod(inc,1),jmod(inc,1)

 9999 CONTINUE
      STOP
      END
