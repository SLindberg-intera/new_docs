c       ************************ PROGRAM inactive_nodes.f ****************************
c          Read input & input.zone and output count of active/inactive nodes for
c          the uppermost five layers.
c
      IMPLICIT DOUBLE PRECISION (A-H,O-Z)
c
      INTEGER, ALLOCATABLE :: zone(:,:,:)
      CHARACTER line*1024
c
      zone=-1000000
c
      OPEN(20,FILE="check_active_inactive.dat",
     >  STATUS='REPLACE',IOSTAT=IST)
c
c --- read input file
c
      WRITE(20,"(a13)") 'Reading input'
      WRITE(20,*)
      OPEN(11,FILE="input",STATUS='OLD'
     >  ,IOSTAT=IST)
      ifnd=0
      DO il=1,1000000
        READ(11,"(a1024)",END=9990) line
        DO iii=1,1000
          IF(line(iii:iii+9).eq."Cartesian,") THEN
            READ(11,*) ni,nj,nk
            ifnd=1
          ENDIF
        ENDDO
        IF(ifnd.ne.0) EXIT
      ENDDO
      CLOSE(11)
      ALLOCATE(zone(ni,nj,nk))
      WRITE(20,"(a16)") 'Number of nodes:'
      WRITE(20,"(a5,i4)") 'nx = ',ni
      WRITE(20,"(a5,i4)") 'ny = ',nj
      WRITE(20,"(a5,i4)") 'nz = ',nk
      WRITE(20,*)
      WRITE(20,*)
      WRITE(20,"(a18)") 'Reading input.zone'
      WRITE(20,*)
c
c --- read input.zone file
c
      OPEN(11,FILE="input.zone",STATUS='OLD'
     >  ,IOSTAT=IST)
      READ(11,*,END=9991) zone
      DO kc=nk,nk-4,-1
	    nact=0
		ninact=0
        DO jc=1,nj
          DO ic=1,ni
            IF(zone(ic,jc,kc).gt.0) THEN
              nact=nact+1
            ELSE
              ninact=ninact+1
            ENDIF
          ENDDO
        ENDDO
        WRITE(20,"(a6,i4,a1,i6,a14,i6,a15)") 'Layer ',kc,':',nact,
     >    ' active nodes,',ninact,' inactive nodes'
      ENDDO
c
      GOTO 9999
 9990 WRITE(*,*) ' Did not find "Cartesian, "',il
c
      GOTO 9999
 9991 WRITE(*,*) ' Read problem with zone file'
c
 9999 CONTINUE
      STOP
      END
