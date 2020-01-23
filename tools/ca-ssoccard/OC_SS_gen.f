c       ************************ PROGRAM OC_SS_gen.f ****************************
c          Read input and input.top files exported from CAST and generate Output
c          Control card for the steady-state simulation.
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      DIMENSION gridxy(500,500,2),laytop(500,500)
      CHARACTER infile1*80,infile2*80,infile3*80,outfile1*80,line*256
      CHARACTER mname*20,date*8,time*10
      CHARACTER(LEN=80) :: comlin1
c
      gridxy=0.0
      laytop=0
c
      infile1="input.sij"
      infile2="input.nij"
      infile3="input.top"
      outfile1="SS_Output_Control.dat"
c
c --- Read model name from command line
c
      comlin1 = ' '
      iarg = 1
      CALL GETARG(iarg,comlin1)
      mname=trim(comlin1)
c
      CALL DATE_AND_TIME (date,time)
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- Determine grid and quadrant center coordinates.
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      READ(11,*) nxs,nys
      nxys=nxs*nys
      xmin=1.0E20
      ymin=1.0E20
      xmax=-1.0E20
      ymax=-1.0E20
c
      DO ii=1,nxys
        READ(11,*) ixs,jys,x,y
        IF(x.lt.xmin) xmin=x
        IF(x.gt.xmax) xmax=x
        IF(y.lt.ymin) ymin=y
        IF(y.gt.ymax) ymax=y
      ENDDO
c
      xlft=xmin+0.25*(xmax-xmin)
      xmid=xmin+0.50*(xmax-xmin)
      xrht=xmin+0.75*(xmax-xmin)
      ybot=ymin+0.25*(ymax-ymin)
      ymid=ymin+0.50*(ymax-ymin)
      ytop=ymin+0.75*(ymax-ymin)
c
      WRITE(*,*) 'XMIN = ',xmin,'  XMAX = ',xmax,'  XLFT = ',
     >  xlft,'  XMID = ',xmid,'  XRHT = ',xrht
      WRITE(*,*) 'YMIN = ',ymin,'  YMAX = ',ymax,'  YBOT = ',
     >  ybot,'  YMID = ',ymid,'  YTOP = ',ytop
c
      CLOSE(11)
c
c --- Determine grid and quadrant center i/j index values.
c
      OPEN(12,FILE=infile2,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      READ(12,*) nxn,nyn
      nxyn=nxn*nyn
      DO ii=1,nxyn
        READ(12,*) ixn,jyn,x,y
        gridxy(ixn,jyn,1)=x
        gridxy(ixn,jyn,2)=y
      ENDDO
c
c --- Find i for left
c
      mindx1=1
      mindx2=1
      xtarg=xlft
      DO ixx=1,nxn
        dist=ABS(gridxy(ixx,1,1)-xtarg)
        d1=ABS(gridxy(mindx1,1,1)-xtarg)
        d2=ABS(gridxy(mindx2,1,1)-xtarg)
        IF(dist.le.d1) THEN
          mindx2=mindx1
          mindx1=ixx
        ELSEIF (dist.le.d2) THEN
          mindx2=ixx
        ENDIF
      ENDDO
c
      d1=ABS(gridxy(mindx1,1,1)-xtarg)
      d2=ABS(gridxy(mindx2,1,1)-xtarg)
      IF(ABS(d1-d2).lt.0.01) THEN
        mindx=min(mindx1,mindx2)
      ELSE
        mindx=mindx1
      ENDIF
      ixlft=mindx
      WRITE(*,*) ' Left X  ',mindx,mindx1,mindx2,gridxy(mindx1,1,1),
     >  gridxy(mindx2,1,1)
c
c --- Find i for center
c
      mindx1=1
      mindx2=1
      xtarg=xmid
      DO ixx=1,nxn
        dist=ABS(gridxy(ixx,1,1)-xtarg)
        d1=ABS(gridxy(mindx1,1,1)-xtarg)
        d2=ABS(gridxy(mindx2,1,1)-xtarg)
        IF(dist.le.d1) THEN
          mindx2=mindx1
          mindx1=ixx
        ELSEIF (dist.le.d2) THEN
          mindx2=ixx
        ENDIF
      ENDDO
c
      d1=ABS(gridxy(mindx1,1,1)-xtarg)
      d2=ABS(gridxy(mindx2,1,1)-xtarg)
      IF(ABS(d1-d2).lt.0.01) THEN
        mindx=min(mindx1,mindx2)
      ELSE
        mindx=mindx1
      ENDIF
      ixmid=mindx
      WRITE(*,*) ' Center X  ',mindx,mindx1,mindx2,gridxy(mindx1,1,1),
     >  gridxy(mindx2,1,1)
c
c --- Find i for right
c
      mindx1=1
      mindx2=1
      xtarg=xrht
      DO ixx=1,nxn
        dist=ABS(gridxy(ixx,1,1)-xtarg)
        d1=ABS(gridxy(mindx1,1,1)-xtarg)
        d2=ABS(gridxy(mindx2,1,1)-xtarg)
        IF(dist.le.d1) THEN
          mindx2=mindx1
          mindx1=ixx
        ELSEIF (dist.le.d2) THEN
          mindx2=ixx
        ENDIF
      ENDDO
c
      d1=ABS(gridxy(mindx1,1,1)-xtarg)
      d2=ABS(gridxy(mindx2,1,1)-xtarg)
      IF(ABS(d1-d2).lt.0.01) THEN
        mindx=max(mindx1,mindx2)
      ELSE
        mindx=mindx1
      ENDIF
      ixrht=mindx
      WRITE(*,*) ' Right X  ',mindx,mindx1,mindx2,gridxy(mindx1,1,1),
     >  gridxy(mindx2,1,1)
c
c --- Find j for bottom
c
      mindy1=1
      mindy2=1
      ytarg=ybot
      DO jyy=1,nyn
        dist=ABS(gridxy(1,jyy,2)-ytarg)
        d1=ABS(gridxy(1,mindy1,2)-ytarg)
        d2=ABS(gridxy(1,mindy2,2)-ytarg)
        IF(dist.le.d1) THEN
          mindy2=mindy1
          mindy1=jyy
        ELSEIF (dist.le.d2) THEN
          mindy2=jyy
        ENDIF
      ENDDO
c
      d1=ABS(gridxy(1,mindy1,2)-ytarg)
      d2=ABS(gridxy(1,mindy2,2)-ytarg)
      IF(ABS(d1-d2).lt.0.01) THEN
        mindy=min(mindy1,mindy2)
      ELSE
        mindy=mindy1
      ENDIF
      jybot=mindy
      WRITE(*,*) ' Bottom Y  ',mindy,mindy1,mindy2,gridxy(1,mindy1,2),
     >  gridxy(1,mindy2,2)
c
c --- Find j for center
c
      mindy1=1
      mindy2=1
      ytarg=ymid
      DO jyy=1,nyn
        dist=ABS(gridxy(1,jyy,2)-ytarg)
        d1=ABS(gridxy(1,mindy1,2)-ytarg)
        d2=ABS(gridxy(1,mindy2,2)-ytarg)
        IF(dist.le.d1) THEN
          mindy2=mindy1
          mindy1=jyy
        ELSEIF (dist.le.d2) THEN
          mindy2=jyy
        ENDIF
      ENDDO
c
      d1=ABS(gridxy(1,mindy1,2)-ytarg)
      d2=ABS(gridxy(1,mindy2,2)-ytarg)
      IF(ABS(d1-d2).lt.0.01) THEN
        mindy=min(mindy1,mindy2)
      ELSE
        mindy=mindy1
      ENDIF
      jymid=mindy
      WRITE(*,*) ' Center Y  ',mindy,mindy1,mindy2,gridxy(1,mindy1,2),
     >  gridxy(1,mindy2,2)
c
c --- Find j for top
c
      mindy1=1
      mindy2=1
      ytarg=ytop
      DO jyy=1,nyn
        dist=ABS(gridxy(1,jyy,2)-ytarg)
        d1=ABS(gridxy(1,mindy1,2)-ytarg)
        d2=ABS(gridxy(1,mindy2,2)-ytarg)
        IF(dist.le.d1) THEN
          mindy2=mindy1
          mindy1=jyy
        ELSEIF (dist.le.d2) THEN
          mindy2=jyy
        ENDIF
      ENDDO
c
      d1=ABS(gridxy(1,mindy1,2)-ytarg)
      d2=ABS(gridxy(1,mindy2,2)-ytarg)
      IF(ABS(d1-d2).lt.0.01) THEN
        mindy=max(mindy1,mindy2)
      ELSE
        mindy=mindy1
      ENDIF
      jytop=mindy
      WRITE(*,*) ' Top Y  ',mindy,mindy1,mindy2,gridxy(1,mindy1,2),
     >  gridxy(1,mindy2,2)
c
      CLOSE(12)
c
c --- Find top active layer for grid and quadrant centers.
c
      OPEN(13,FILE=infile3,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      DO ii=1,nxyn
        READ(13,*) ixn,jyn,itop
        laytop(ixn,jyn)=itop
      ENDDO
c
      ltmid=laytop(ixmid,jymid)
      ltq1=laytop(ixrht,jytop)
      ltq2=laytop(ixlft,jytop)
      ltq3=laytop(ixlft,jybot)
      ltq4=laytop(ixrht,jybot)
c
      WRITE(*,*) ' Center  ',ixmid,jymid,gridxy(ixmid,jymid,1),
     >  gridxy(ixmid,jymid,2),ltmid
      WRITE(*,*) ' Q1  ',ixrht,jytop,gridxy(ixrht,jytop,1),
     >  gridxy(ixrht,jytop,2),ltq1
      WRITE(*,*) ' Q2  ',ixlft,jytop,gridxy(ixlft,jytop,1),
     >  gridxy(ixlft,jytop,2),ltq2
      WRITE(*,*) ' Q3  ',ixlft,jybot,gridxy(ixlft,jybot,1),
     >  gridxy(ixlft,jybot,2),ltq3
      WRITE(*,*) ' Q4  ',ixrht,jybot,gridxy(ixrht,jybot,1),
     >  gridxy(ixrht,jybot,2),ltq4
c
      IF(MOD(ltmid,20).lt.0.01) THEN
        nummid=ltmid/20+1
      ELSE
        nummid=ltmid/20+2
      ENDIF
c
      IF(MOD(ltq1,20).lt.0.01) THEN
        numq1=ltq1/20+1
      ELSE
        numq1=ltq1/20+2
      ENDIF
c
      IF(MOD(ltq2,20).lt.0.01) THEN
        numq2=ltq2/20+1
      ELSE
        numq2=ltq2/20+2
      ENDIF
c
      IF(MOD(ltq3,20).lt.0.01) THEN
        numq3=ltq3/20+1
      ELSE
        numq3=ltq3/20+2
      ENDIF
c
      IF(MOD(ltq4,20).lt.0.01) THEN
        numq4=ltq4/20+1
      ELSE
        numq4=ltq4/20+2
      ENDIF
c
      numlay=nummid+numq1+numq2+numq3+numq4
      WRITE(*,*) ' Number  ',numlay,nummid,numq1,numq2,numq3,numq4
c
c --- Write Output Control Card.
c
      WRITE(20,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(20,"(a)") '#'
      WRITE(20,"(a30,a23,a)") '# Output Control Card for the ',
     >  'steady-state model for ',ADJUSTL(TRIM(mname))
      WRITE(20,"(a)") '#'
      WRITE(20,"(3a)") '# Steady-state Output Control Card generated ',
     >  'by OC_SS_gen_olive.exe ',
     >  ' Version 1.0 - 11-8-2019'
      WRITE(20,"(12a)") '# Run on ',date(5:6),'-',
     >  date(7:8),'-',date(1:4),' at ',time(1:2),':',
     >  time(3:4),':',time(5:6)
      WRITE(20,"(a)") '#'
      WRITE(20,"(2a)") '# Reference node profiles in the center of ',
     >  'the model domain and in'
      WRITE(20,"(a)") '# the center of each quadrant.'
      WRITE(20,"(a)") '#'
      WRITE(20,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(20,"(a)") '~Output Control Card'
      WRITE(20,"(i3,a1)") numlay+1,','
      WRITE(20,"(a)") '#Southwest corner node'
      WRITE(20,"(a)") ' 1, 1, 1,'
      WRITE(20,"(a)") '#Center domain'
      WRITE(20,"(3(i3,a2))") ixmid,', ',jymid,', ',ltmid,', '
      IF(MOD(ltmid,20).lt.0.01) THEN
        last=ltmid-20
      ELSE
        last=20*(ltmid/20)
      ENDIF
      DO k=last,1,-20
        WRITE(20,"(3(i3,a2))") ixmid,', ',jymid,', ',k,', '
      ENDDO
      WRITE(20,"(3(i3,a2))") ixmid,', ',jymid,', ',1,', '
c
      WRITE(20,"(a)") '#Center first quadrant (upper right hand)'
      WRITE(20,"(3(i3,a2))") ixrht,', ',jytop,', ',ltq1,', '
      IF(MOD(ltq1,20).lt.0.01) THEN
        last=ltq1-20
      ELSE
        last=20*(ltq1/20)
      ENDIF
      DO k=last,1,-20
        WRITE(20,"(3(i3,a2))") ixrht,', ',jytop,', ',k,', '
      ENDDO
      WRITE(20,"(3(i3,a2))") ixrht,', ',jytop,', ',1,', '
c
      WRITE(20,"(a)") '#Center second quadrant (upper left hand)'
      WRITE(20,"(3(i3,a2))") ixlft,', ',jytop,', ',ltq2,', '
      IF(MOD(ltq2,20).lt.0.01) THEN
        last=ltq2-20
      ELSE
        last=20*(ltq2/20)
      ENDIF
      DO k=last,1,-20
        WRITE(20,"(3(i3,a2))") ixlft,', ',jytop,', ',k,', '
      ENDDO
      WRITE(20,"(3(i3,a2))") ixlft,', ',jytop,', ',1,', '
c
      WRITE(20,"(a)") '#Center third quadrant (lower left hand)'
      WRITE(20,"(3(i3,a2))") ixlft,', ',jybot,', ',ltq3,', '
      IF(MOD(ltq3,20).lt.0.01) THEN
        last=ltq3-20
      ELSE
        last=20*(ltq3/20)
      ENDIF
      DO k=last,1,-20
        WRITE(20,"(3(i3,a2))") ixlft,', ',jybot,', ',k,', '
      ENDDO
      WRITE(20,"(3(i3,a2))") ixlft,', ',jybot,', ',1,', '
c
      WRITE(20,"(a)") '#Center fourth quadrant (lower right hand)'
      WRITE(20,"(3(i3,a2))") ixrht,', ',jybot,', ',ltq4,', '
      IF(MOD(ltq4,20).lt.0.01) THEN
        last=ltq4-20
      ELSE
        last=20*(ltq4/20)
      ENDIF
      DO k=last,1,-20
        WRITE(20,"(3(i3,a2))") ixrht,', ',jybot,', ',k,', '
      ENDDO
      WRITE(20,"(3(i3,a2))") ixrht,', ',jybot,', ',1,', '
c
      WRITE(20,"(a)") '10, 1, year, m, 8, 8, 8,'
      WRITE(20,"(a)") '10,'
      WRITE(20,"(a)") 'Rock/Soil Type, ,'
      WRITE(20,"(a)") 'Integrated Water Mass, kg, ,'
      WRITE(20,"(a)") 'Aqueous Saturation, ,'
      WRITE(20,"(a)") 'Aqueous Moisture Content, ,'
      WRITE(20,"(a)") 'Aqueous Pressure, Pa,'
      WRITE(20,"(a)") 'Aqueous Hydraulic Head, m,'
      WRITE(20,"(a)") 'Diffusive Porosity, ,'
      WRITE(20,"(a)")
     >  'XNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(20,"(a)")
     >  'YNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(20,"(a)")
     >  'ZNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(20,"(a)") '1,'
      WRITE(20,"(a)") '10000, year,'
      WRITE(20,"(a)") '10,'
      WRITE(20,"(a)") 'Rock/Soil Type, ,'
      WRITE(20,"(a)") 'Aqueous Saturation, ,'
      WRITE(20,"(a)") 'Aqueous Moisture Content, ,'
      WRITE(20,"(a)") 'Aqueous Pressure, Pa,'
      WRITE(20,"(a)") 'Aqueous Hydraulic Head, m,'
      WRITE(20,"(a)") 'Diffusive Porosity, ,'
      WRITE(20,"(a)")
     >  'XNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(20,"(a)")
     >  'YNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(20,"(a)")
     >  'ZNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(20,"(a)") 'Final Restart, ,'
c
      WRITE(20,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
 9999 CONTINUE
      STOP
      END
