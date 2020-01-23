c       ************************ PROGRAM OC_rad1_gen.f ****************************
c          Generate Output Control card for the rad transport simulations.
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      DIMENSION sitexy(500,2),ehxy(5000,2),ifound(500),ipltyr(100)
      DIMENSION gridxy(500,500,2),laytop(500,500)
      DIMENSION mindxs(500),mindys(500)
      CHARACTER mname*20
      CHARACTER infile1*80,infile2*80,infile3*80
      CHARACTER infile4*80,infile5*80,infile6*80
      CHARACTER outfile1*80,outfile2*80,outfile3*80
      CHARACTER line*256,comm*22,radch*1
      CHARACTER site(500)*20,ehsite(5000)*20
      CHARACTER(LEN=80) :: comlin1
      CHARACTER(LEN=80) :: comlin2
c
      site=""
      ehsite=""
      sitexy=0.0
      ehxy=0.0
      gridxy=0.0
      ifound=0
      laytop=0
c
      infile1="../sources/rads1-src.ref"
      infile2="../../commondata/ehsit_01122018_centroid.prn"
      infile3="../build/input.nij"
      infile4="../build/input.top"
      infile5="plot_times.txt"
      infile6="../build/input.sij"
c
c --- Read model name from command line
c
      comlin1 = ' '
      iarg = 1
      CALL GETARG(iarg,comlin1)
      mname=trim(comlin1)
c
c
c --- Read switch for rad1/rad2 from command line
c
      comlin2 = ' '
      iarg = 2
      CALL GETARG(iarg,comlin2)
      READ(comlin2,"(i1)") irad
      IF((irad.ne.1).and.(irad.ne.2)) GOTO 9991
      WRITE(radch,"(i1)") irad
      WRITE(*,"(a,i1)") ' Output for rad',irad
c
      outfile1="rad"//radch//"_Output_Control_check.dat"
      outfile2="rad"//radch//"_Output_Control.dat"
      outfile3="rad"//radch//"_Mass_Balance_Output_Control.dat"
      WRITE(*,*) outfile1
      WRITE(*,*) outfile2
c
      OPEN(20,FILE=outfile1,
     >  STATUS='REPLACE',IOSTAT=IST)
      WRITE(20,"(2a)") 'Site                         Cent_X         ',
     >  'Cent_Y    i    j         Node_X         Node_Y       Distance'
c
      OPEN(21,FILE=outfile2,
     >  STATUS='REPLACE',IOSTAT=IST)
c
      OPEN(22,FILE=outfile3,
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- Determine grid and quadrant center coordinates.
c
      OPEN(16,FILE=infile6,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      READ(16,*) nxs,nys
      nxys=nxs*nys
      xmin=1.0E20
      ymin=1.0E20
      xmax=-1.0E20
      ymax=-1.0E20
c
      DO ii=1,nxys
        READ(16,*) ixs,jys,x,y
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
      CLOSE(16)
c
c --- Read source site list.
c
      OPEN(11,FILE=infile1,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      nsite=1
  100 READ(11,"(a256)",END=200) line
      DO jj=1,200
        IF(line(jj:jj+4).eq."-Part") GOTO 100
      ENDDO
      IF(line(1:9).ne."# Site = ") GOTO 9990
      ndch=LEN(TRIM(line))
      WRITE(*,*) nsite,ndch,line(10:ndch)
      site(nsite)=line(10:ndch)
      nsite=nsite+1
      GOTO 100
c
  200 nsite=nsite-1
      CLOSE(11)
c
c --- Read source site centroids.
c
      OPEN(12,FILE=infile2,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      nseh=1
      READ(12,*)
  210 READ(12,"(a20,40x,2f20.0)",END=300) ehsite(nseh),ehxy(nseh,1),
     >  ehxy(nseh,2)
c      WRITE(20,*) nseh,ehsite(nseh),ehxy(nseh,1),ehxy(nseh,2)
      nseh=nseh+1
      GOTO 210
c
  300 nseh=nseh-1
      CLOSE(12)
      WRITE(*,*) ' Finished centroids ',nseh
c
c --- Get site XYs from ehsite XYs
c
      DO is=1,nsite
        DO ie=1,nseh
          IF(site(is)(1:20).eq.ehsite(ie)(1:20)) THEN
            sitexy(is,1)=ehxy(ie,1)
            sitexy(is,2)=ehxy(ie,2)
            ifound(is)=1
          ENDIF
        ENDDO
      ENDDO
      WRITE(*,*) ' Matched XYs from ehsit'
c
c --- Read model i/j & x/y values.
c
      OPEN(13,FILE=infile3,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      READ(13,*) nxn,nyn
      nxyn=nxn*nyn
      DO ii=1,nxyn
        READ(13,*) ixn,jyn,x,y
        gridxy(ixn,jyn,1)=x
        gridxy(ixn,jyn,2)=y
      ENDDO
      WRITE(*,*) ' Read node XYs'
      CLOSE(13)
c
c --- Find i&j for centroids
c
      mindxs=0
      mindys=0
      DO is=1,nsite
        dmin=1000000.0
        DO ixx=1,nxn
          DO iyy=1,nyn
            dist=SQRT((gridxy(ixx,iyy,1)-sitexy(is,1))**2+
     >                (gridxy(ixx,iyy,2)-sitexy(is,2))**2)
            IF(dist.le.dmin) THEN
              mindxs(is)=ixx
              mindys(is)=iyy
              dmin=dist
            ENDIF
          ENDDO
        ENDDO
c
        IF(ifound(is).eq.0) THEN
          WRITE(20,"(3a)") '------------------------------------------',
     >      '---------------------------------------------------------',
     >      '------------------'
          WRITE(20,"(3a)") '------------------------------------------',
     >      '---------------------------------------------------------',
     >      '------------------'
          WRITE(20,"(4a)") '******* Site ',site(is),' was not found in',
     >      ' ehsit centroid file.'
          WRITE(20,"(3a)") '------------------------------------------',
     >      '---------------------------------------------------------',
     >      '------------------'
          WRITE(20,"(3a)") '------------------------------------------',
     >      '---------------------------------------------------------',
     >      '------------------'
        ELSE
          WRITE(20,"(a20,2f15.6,2i5,3f15.6)") site(is),sitexy(is,1),
     >      sitexy(is,2),mindxs(is),mindys(is),gridxy(mindxs(is),
     >      mindys(is),1),gridxy(mindxs(is),mindys(is),2),dmin
          IF(dmin.gt.25) THEN
            WRITE(20,"(3a)") '----------------------------------------',
     >        '-------------------------------------------------------',
     >        '----------------------'
            WRITE(20,"(3a)") '----------------------------------------',
     >        '-------------------------------------------------------',
     >        '----------------------'
            WRITE(20,"(5a)") '******* Site ',site(is),' centroid is',
     >        ' more than 25 m from closest i/j. May need to adjust',
     >        ' i/j for this site.'
            WRITE(20,"(3a)") '----------------------------------------',
     >        '-------------------------------------------------------',
     >        '----------------------'
            WRITE(20,"(3a)") '----------------------------------------',
     >        '-------------------------------------------------------',
     >        '----------------------'
          ENDIF
        ENDIF
      ENDDO
c
c --- Determine grid and quadrant center i/j index values.
c
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
c --- Read top active layer node k for model.
c
      OPEN(14,FILE=infile4,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      DO ii=1,nxyn
        READ(14,*) ixn,jyn,itop
        laytop(ixn,jyn)=itop
      ENDDO
c
c Assign top elevations
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
      nrefn=0
      DO is=1,nsite
        IF(ifound(is).eq.1) nrefn=nrefn+1
      ENDDO
c
c --- Read plot times.
c
      CLOSE(14)
      OPEN(15,FILE=infile5,STATUS='OLD'
     >  ,IOSTAT=IST)
c
      ipltyr=0
      nyr=1
  400 READ(15,*,END=500) ipltyr(nyr)
      nyr=nyr+1
      GOTO 400
c
  500 nyr=nyr-1
      CLOSE(15)
      WRITE(*,*) ' Found ',nyr,' times'
c
c --- Write Output Control Card.
c
      WRITE(21,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(21,"(a)") '#'
      WRITE(21,"(4a)") '# Output Control Card for the rad',radch,
     >  ' model for ',mname
      WRITE(21,"(a)") '#'
      WRITE(21,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(21,"(a)") '~Output Control Card'
      WRITE(21,"(i3,a1)") nrefn+numlay,','
      WRITE(21,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(21,"(a)") '#'
      WRITE(21,"(2a)") '# Reference node profiles at waste site',
     >  ' centriods.'
      WRITE(21,"(a)") '#'
      WRITE(21,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
c
      DO is=1,nsite
        IF(ifound(is).eq.1) THEN
          comm="#"//trim(site(is))
          WRITE(21,"(a)") comm
          WRITE(21,"(3(i3,a2))") mindxs(is),', ',mindys(is),', ',
     >      laytop(mindxs(is),mindys(is)),', '
        ENDIF
      ENDDO
c
      WRITE(21,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(21,"(a)") '#'
      WRITE(21,"(2a)") '# Reference node profiles in the center of ',
     >  'the model domain and in'
      WRITE(21,"(a)") '# the center of each quadrant.'
      WRITE(21,"(a)") '#'
      WRITE(21,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
c
      WRITE(21,"(a)") '#Center domain'
      WRITE(21,"(3(i3,a2))") ixmid,', ',jymid,', ',ltmid,', '
      IF(MOD(ltmid,20).lt.0.01) THEN
        last=ltmid-20
      ELSE
        last=20*(ltmid/20)
      ENDIF
      DO k=last,1,-20
        WRITE(21,"(3(i3,a2))") ixmid,', ',jymid,', ',k,', '
      ENDDO
      WRITE(21,"(3(i3,a2))") ixmid,', ',jymid,', ',1,', '
c
      WRITE(21,"(a)") '#Center first quadrant (upper right hand)'
      WRITE(21,"(3(i3,a2))") ixrht,', ',jytop,', ',ltq1,', '
      IF(MOD(ltq1,20).lt.0.01) THEN
        last=ltq1-20
      ELSE
        last=20*(ltq1/20)
      ENDIF
      DO k=last,1,-20
        WRITE(21,"(3(i3,a2))") ixrht,', ',jytop,', ',k,', '
      ENDDO
      WRITE(21,"(3(i3,a2))") ixrht,', ',jytop,', ',1,', '
c
      WRITE(21,"(a)") '#Center second quadrant (upper left hand)'
      WRITE(21,"(3(i3,a2))") ixlft,', ',jytop,', ',ltq2,', '
      IF(MOD(ltq2,20).lt.0.01) THEN
        last=ltq2-20
      ELSE
        last=20*(ltq2/20)
      ENDIF
      DO k=last,1,-20
        WRITE(21,"(3(i3,a2))") ixlft,', ',jytop,', ',k,', '
      ENDDO
      WRITE(21,"(3(i3,a2))") ixlft,', ',jytop,', ',1,', '
c
      WRITE(21,"(a)") '#Center third quadrant (lower left hand)'
      WRITE(21,"(3(i3,a2))") ixlft,', ',jybot,', ',ltq3,', '
      IF(MOD(ltq3,20).lt.0.01) THEN
        last=ltq3-20
      ELSE
        last=20*(ltq3/20)
      ENDIF
      DO k=last,1,-20
        WRITE(21,"(3(i3,a2))") ixlft,', ',jybot,', ',k,', '
      ENDDO
      WRITE(21,"(3(i3,a2))") ixlft,', ',jybot,', ',1,', '
c
      WRITE(21,"(a)") '#Center fourth quadrant (lower right hand)'
      WRITE(21,"(3(i3,a2))") ixrht,', ',jybot,', ',ltq4,', '
      IF(MOD(ltq4,20).lt.0.01) THEN
        last=ltq4-20
      ELSE
        last=20*(ltq4/20)
      ENDIF
      DO k=last,1,-20
        WRITE(21,"(3(i3,a2))") ixrht,', ',jybot,', ',k,', '
      ENDDO
      WRITE(21,"(3(i3,a2))") ixrht,', ',jybot,', ',1,', '
c
      WRITE(21,"(a)") '1, 1, year, m, 8, 8, 8,'
      WRITE(21,"(a)") '25,'
      WRITE(21,"(a)") 'Rock/Soil Type, ,'
      WRITE(21,"(a)") 'Integrated Water Mass, kg,'
      IF(irad.eq.1) THEN
        WRITE(21,"(a)") 'Solute Aqueous Conc, C-14,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, C-14, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Cl-36,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, Cl-36, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, H-3,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, H-3, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, I-129,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, I-129, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Np-237,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, Np-237, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Re-187,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, Re-187, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Sr-90,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, Sr-90, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Tc-99,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, Tc-99, ,'
      ELSE
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-232,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, U-232, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-233,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, U-233, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-234,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, U-234, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-235,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, U-235, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-236,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, U-236, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-238,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, U-238, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Th-230,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, Th-230, ,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Ra-226,1/L,'
        WRITE(21,"(a)") 'Solute Integrated Mass, Ra-226, ,'
      ENDIF
      WRITE(21,"(a)") 'Aqueous Saturation, ,'
      WRITE(21,"(a)") 'Aqueous Moisture Content, ,'
      WRITE(21,"(a)") 'Aqueous Pressure, Pa,'
      WRITE(21,"(a)") 'Aqueous Hydraulic Head, m,'
      WRITE(21,"(a)")
     >  'XNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(21,"(a)")
     >  'YNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(21,"(a)")
     >  'ZNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(21,"(i3,a1)") nyr,','
      DO iy=1,nyr
        IF(ipltyr(iy).le.9999) THEN
          WRITE(21,"(i4,a7)") ipltyr(iy),', year,'
        ELSE
          WRITE(21,"(i5,a7)") ipltyr(iy),', year,'
        ENDIF
      ENDDO
      WRITE(21,"(a)") '17,'
      WRITE(21,"(a)") 'Rock/Soil Type, ,'
      IF(irad.eq.1) THEN
        WRITE(21,"(a)") 'Solute Aqueous Conc, C-14,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Cl-36,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, H-3,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, I-129,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Np-237,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Re-187,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Sr-90,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Tc-99,1/L,'
      ELSE
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-232,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-233,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-234,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-235,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-236,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, U-238,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Th-230,1/L,'
        WRITE(21,"(a)") 'Solute Aqueous Conc, Ra-226,1/L,'
      ENDIF
      WRITE(21,"(a)") 'Aqueous Saturation, ,'
      WRITE(21,"(a)") 'Aqueous Moisture Content, ,'
      WRITE(21,"(a)") 'Aqueous Pressure, Pa,'
      WRITE(21,"(a)") 'Aqueous Hydraulic Head, m,'
      WRITE(21,"(a)")
     >  'XNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(21,"(a)")
     >  'YNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(21,"(a)")
     >  'ZNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(21,"(a)")
     >  'No Restart, ,'
c
      WRITE(21,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
c
c --- Write MB run Output Control Card.
c
      WRITE(22,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(22,"(a)") '#'
      WRITE(22,"(4a)") '# Output Control Card for the rad',radch,
     >  ' mass balance model for ',mname
      WRITE(22,"(a)") '#'
      WRITE(22,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(22,"(a)") '~Output Control Card'
      WRITE(22,"(i3,a1)") numlay,','
      WRITE(22,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
      WRITE(22,"(a)") '#'
      WRITE(22,"(2a)") '# Reference node profiles in the center of ',
     >  'the model domain and in'
      WRITE(22,"(a)") '# the center of each quadrant.'
      WRITE(22,"(a)") '#'
      WRITE(22,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
c
      WRITE(22,"(a)") '#Center domain'
      WRITE(22,"(3(i3,a2))") ixmid,', ',jymid,', ',ltmid,', '
      IF(MOD(ltmid,20).lt.0.01) THEN
        last=ltmid-20
      ELSE
        last=20*(ltmid/20)
      ENDIF
      DO k=last,1,-20
        WRITE(22,"(3(i3,a2))") ixmid,', ',jymid,', ',k,', '
      ENDDO
      WRITE(22,"(3(i3,a2))") ixmid,', ',jymid,', ',1,', '
c
      WRITE(22,"(a)") '#Center first quadrant (upper right hand)'
      WRITE(22,"(3(i3,a2))") ixrht,', ',jytop,', ',ltq1,', '
      IF(MOD(ltq1,20).lt.0.01) THEN
        last=ltq1-20
      ELSE
        last=20*(ltq1/20)
      ENDIF
      DO k=last,1,-20
        WRITE(22,"(3(i3,a2))") ixrht,', ',jytop,', ',k,', '
      ENDDO
      WRITE(22,"(3(i3,a2))") ixrht,', ',jytop,', ',1,', '
c
      WRITE(22,"(a)") '#Center second quadrant (upper left hand)'
      WRITE(22,"(3(i3,a2))") ixlft,', ',jytop,', ',ltq2,', '
      IF(MOD(ltq2,20).lt.0.01) THEN
        last=ltq2-20
      ELSE
        last=20*(ltq2/20)
      ENDIF
      DO k=last,1,-20
        WRITE(22,"(3(i3,a2))") ixlft,', ',jytop,', ',k,', '
      ENDDO
      WRITE(22,"(3(i3,a2))") ixlft,', ',jytop,', ',1,', '
c
      WRITE(22,"(a)") '#Center third quadrant (lower left hand)'
      WRITE(22,"(3(i3,a2))") ixlft,', ',jybot,', ',ltq3,', '
      IF(MOD(ltq3,20).lt.0.01) THEN
        last=ltq3-20
      ELSE
        last=20*(ltq3/20)
      ENDIF
      DO k=last,1,-20
        WRITE(22,"(3(i3,a2))") ixlft,', ',jybot,', ',k,', '
      ENDDO
      WRITE(22,"(3(i3,a2))") ixlft,', ',jybot,', ',1,', '
c
      WRITE(22,"(a)") '#Center fourth quadrant (lower right hand)'
      WRITE(22,"(3(i3,a2))") ixrht,', ',jybot,', ',ltq4,', '
      IF(MOD(ltq4,20).lt.0.01) THEN
        last=ltq4-20
      ELSE
        last=20*(ltq4/20)
      ENDIF
      DO k=last,1,-20
        WRITE(22,"(3(i3,a2))") ixrht,', ',jybot,', ',k,', '
      ENDDO
      WRITE(22,"(3(i3,a2))") ixrht,', ',jybot,', ',1,', '
c
      WRITE(22,"(a)") '1, 1, year, m, 8, 8, 8,'
      WRITE(22,"(a)") '25,'
      WRITE(22,"(a)") 'Rock/Soil Type, ,'
      WRITE(22,"(a)") 'Integrated Water Mass, kg,'
      IF(irad.eq.1) THEN
        WRITE(22,"(a)") 'Solute Aqueous Conc, C-14,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, C-14, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Cl-36,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, Cl-36, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, H-3,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, H-3, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, I-129,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, I-129, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Np-237,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, Np-237, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Re-187,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, Re-187, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Sr-90,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, Sr-90, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Tc-99,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, Tc-99, ,'
      ELSE
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-232,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, U-232, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-233,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, U-233, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-234,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, U-234, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-235,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, U-235, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-236,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, U-236, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-238,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, U-238, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Th-230,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, Th-230, ,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Ra-226,1/L,'
        WRITE(22,"(a)") 'Solute Integrated Mass, Ra-226, ,'
      ENDIF
      WRITE(22,"(a)") 'Aqueous Saturation, ,'
      WRITE(22,"(a)") 'Aqueous Moisture Content, ,'
      WRITE(22,"(a)") 'Aqueous Pressure, Pa,'
      WRITE(22,"(a)") 'Aqueous Hydraulic Head, m,'
      WRITE(22,"(a)")
     >  'XNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(22,"(a)")
     >  'YNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(22,"(a)")
     >  'ZNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(22,"(i3,a1)") 1,','
      WRITE(22,"(a12)") '22222, year,'
      WRITE(22,"(a)") '16,'
      WRITE(22,"(a)") 'Rock/Soil Type, ,'
      IF(irad.eq.1) THEN
        WRITE(22,"(a)") 'Solute Aqueous Conc, C-14,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Cl-36,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, H-3,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, I-129,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Np-237,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Re-187,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Sr-90,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Tc-99,1/L,'
      ELSE
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-232,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-233,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-234,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-235,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-236,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, U-238,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Th-230,1/L,'
        WRITE(22,"(a)") 'Solute Aqueous Conc, Ra-226,1/L,'
      ENDIF
      WRITE(22,"(a)") 'Aqueous Saturation, ,'
      WRITE(22,"(a)") 'Aqueous Moisture Content, ,'
      WRITE(22,"(a)") 'Aqueous Pressure, Pa,'
      WRITE(22,"(a)") 'Aqueous Hydraulic Head, m,'
      WRITE(22,"(a)")
     >  'XNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(22,"(a)")
     >  'YNC Aqueous Volumetric Flux (Node Centered), mm/year,'
      WRITE(22,"(a)")
     >  'ZNC Aqueous Volumetric Flux (Node Centered), mm/year,'
c
      WRITE(22,"(2a)") '#-------------------------------------------',
     >  '-----------------------'
c
      GOTO 9999
 9990 WRITE(20,*) ' Format problem in ref file: ',infile1
      GOTO 9999
c
 9991 WRITE(*,*) ' Invalid rad1/2 switch: ',irad
      GOTO 9999
c
 9999 CONTINUE
      STOP
      END
