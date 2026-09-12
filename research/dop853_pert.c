
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
/* EXP-FLOOR-01 kc 对拍器 — lgt 独立栈 DOP853 C 实现(与 scipy 同算法系数/控制律)
   IC 逐字节 = ci-control/bridge/research/exp-floor-01-lgt-ic-hex.json (ic_float.hex)
   MS/ME 由 Python 端 %.17g 注入,与 scipy 端逐位同 */
static const double MS_ = 39.478417604357432;
static const double ME_ = 0.00011855368806588536;
static double Y0[18] = {
  0x0.0p+0, 0x0.0p+0, 0x0.0p+0,
  0x1.0000000000000p+0, 0x0.0p+0, 0x0.0p+0,
  0x1.00a86d71f3626p+0, 0x0.0p+0, 0x0.0p+0,
  -0x0.0p+0, -0x1.dda4d8c175e05p-16, -0x0.0p+0,
  0x0.0p+0, 0x1.921fb54442d18p+2, 0x0.0p+0,
  0x0.0p+0, 0x1.9fdea3efb987ap+2, 0x0.0p+0 };
static const double C2=0.05260015195876773, C3=0.0789002279381516, C4=0.1183503419072274,
 C5=0.2816496580927726, C6=0.3333333333333333, C7=0.25, C8=0.3076923076923077,
 C9=0.6512820512820513, C10=0.6, C11=0.8571428571428571;
static const double A21=0.05260015195876773;
static const double A31=0.0197250569845379, A32=0.0591751709536137;
static const double A41=0.02958758547680685, A43=0.08876275643042054;
static const double A51=0.2413651341592667, A53=-0.8845494793282861, A54=0.924834003261792;
static const double A61=0.037037037037037035, A64=0.17082860872947386, A65=0.12546768756682242;
static const double A71=0.037109375, A74=0.17025221101954405, A75=0.06021653898045596, A76=-0.017578125;
static const double A81=0.03709200011850479, A84=0.17038392571223998, A85=0.10726203044637328,
 A86=-0.015319437748624402, A87=0.008273789163814023;
static const double A91=0.6241109587160757, A94=-3.3608926294469414, A95=-0.868219346841726,
 A96=27.59209969944671, A97=20.154067550477894, A98=-43.48988418106996;
static const double A101=0.47766253643826434, A104=-2.4881146199716677, A105=-0.590290826836843,
 A106=21.230051448181193, A107=15.279233632882423, A108=-33.28821096898486, A109=-0.020331201708508627;
static const double A111=-0.9371424300859873, A114=5.186372428844064, A115=1.0914373489967295,
 A116=-8.149787010746927, A117=-18.52006565999696, A118=22.739487099350505, A119=2.4936055526796523,
 A1110=-3.0467644718982196;
static const double A121=2.273310147516538, A124=-10.53449546673725, A125=-2.0008720582248625,
 A126=-17.9589318631188, A127=27.94888452941996, A128=-2.8589982771350235, A129=-8.87285693353063,
 A1210=12.360567175794303, A1211=0.6433927460157636;
static const double B1=0.054293734116568765, B6=4.450312892752409, B7=1.8915178993145003,
 B8=-5.801203960010585, B9=0.3111643669578199, B10=-0.1521609496625161, B11=0.20136540080403034,
 B12=0.04471061572777259;
static const double E51=0.01312004499419488, E56=-1.2251564463762044, E57=-0.4957589496572502,
 E58=1.6643771824549864, E59=-0.35032884874997366, E510=0.3341791187130175, E511=0.08192320648511571,
 E512=-0.022355307863886294;
static const double E31=-0.18980075407240762, E36=4.450312892752409, E37=1.8915178993145003,
 E38=-5.801203960010585, E39=-0.4226823213237919, E310=-0.1521609496625161, E311=0.20136540080403034,
 E312=0.02265179219836082;
#define SAFETY 0.9
#define MIN_FACTOR 0.2
#define MAX_FACTOR 10.0
static double MM_;
static long NFEV=0;
static inline void rhs(const double*y,double*k){
  NFEV++;
  double dSEx=y[3]-y[0],dSEy=y[4]-y[1],dSEz=y[5]-y[2];
  double dSMx=y[6]-y[0],dSMy=y[7]-y[1],dSMz=y[8]-y[2];
  double dEMx=y[6]-y[3],dEMy=y[7]-y[4],dEMz=y[8]-y[5];
  double rSE2=dSEx*dSEx+dSEy*dSEy+dSEz*dSEz, rSM2=dSMx*dSMx+dSMy*dSMy+dSMz*dSMz, rEM2=dEMx*dEMx+dEMy*dEMy+dEMz*dEMz;
  double iSE=1.0/(rSE2*sqrt(rSE2)), iSM=1.0/(rSM2*sqrt(rSM2)), iEM=1.0/(rEM2*sqrt(rEM2));
  double cSE=ME_*iSE, cSM=MM_*iSM, cEM1=MS_*iSE, cEM2=MM_*iEM, cSM1=MS_*iSM, cEM3=ME_*iEM;
  k[0]=y[9]; k[1]=y[10]; k[2]=y[11]; k[3]=y[12]; k[4]=y[13]; k[5]=y[14]; k[6]=y[15]; k[7]=y[16]; k[8]=y[17];
  k[9]= cSE*dSEx + cSM*dSMx;  k[10]=cSE*dSEy + cSM*dSMy;  k[11]=cSE*dSEz + cSM*dSMz;
  k[12]=-cEM1*dSEx + cEM2*dEMx; k[13]=-cEM1*dSEy + cEM2*dEMy; k[14]=-cEM1*dSEz + cEM2*dEMz;
  k[15]=-cSM1*dSMx - cEM3*dEMx; k[16]=-cSM1*dSMy - cEM3*dEMy; k[17]=-cSM1*dSMz - cEM3*dEMz;
}
static unsigned long long SM64;
static double urand(void){ SM64+=0x9E3779B97F4A7C15ULL; unsigned long long z=SM64;
  z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; z=z^(z>>31);
  return (double)(z>>11)*(1.0/9007199254740992.0); }
int main(int argc,char**argv){
  double K=atof(argv[1]); int NORB=atoi(argv[2]); int SPO=atoi(argv[3]);
  const char*outp=argv[4];
  double EPS=(argc>5)?atof(argv[5]):0.0; unsigned long long SEED=(argc>6)?strtoull(argv[6],0,10):1ULL;
  SM64=SEED;
  MM_=K*0.0123*ME_;
  double RTOL=1e-9, ATOL=1e-14;
  double T_ORB=2.0*M_PI;
  double ds=T_ORB/SPO;
  double y[18]; for(int i=0;i<18;i++) y[i]=Y0[i]*(1.0+EPS*(2.0*urand()-1.0));
  double Kk[13][18], yt[18], ynew[18];
  double t=0.0, h=1e-4;
  FILE*f=fopen(outp,"w");
  fprintf(f,"{\"k\":%g,\"MM_over_ME\":%.17g,\"norb\":%d,\"spo\":%d,\"eps\":%.3g,\"seed\":%llu,\"rtol\":1e-9,\"atol\":1e-14,\"T_ORB\":\"2pi\",",K,MM_/ME_,NORB,SPO,EPS,SEED);
  fprintf(f,"\"floors_per_orb\":[");
  double gmin=1e30; int g_orb=-1;
  for(int orb=0;orb<NORB;orb++){
    double rmin=1e30;
    for(int s=0;s<SPO;s++){
      double t_end=(orb*SPO+s+1)*ds;
      while(t<t_end){
        double hh=h; if(t+hh>t_end) hh=t_end-t;
        /* DOP853 12 段 */
        rhs(y,Kk[0]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A21*Kk[0][i]);
        rhs(yt,Kk[1]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A31*Kk[0][i]+A32*Kk[1][i]);
        rhs(yt,Kk[2]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A41*Kk[0][i]+A43*Kk[2][i]);
        rhs(yt,Kk[3]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A51*Kk[0][i]+A53*Kk[2][i]+A54*Kk[3][i]);
        rhs(yt,Kk[4]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A61*Kk[0][i]+A64*Kk[3][i]+A65*Kk[4][i]);
        rhs(yt,Kk[5]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A71*Kk[0][i]+A74*Kk[3][i]+A75*Kk[4][i]+A76*Kk[5][i]);
        rhs(yt,Kk[6]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A81*Kk[0][i]+A84*Kk[3][i]+A85*Kk[4][i]+A86*Kk[5][i]+A87*Kk[6][i]);
        rhs(yt,Kk[7]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A91*Kk[0][i]+A94*Kk[3][i]+A95*Kk[4][i]+A96*Kk[5][i]+A97*Kk[6][i]+A98*Kk[7][i]);
        rhs(yt,Kk[8]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A101*Kk[0][i]+A104*Kk[3][i]+A105*Kk[4][i]+A106*Kk[5][i]+A107*Kk[6][i]+A108*Kk[7][i]+A109*Kk[8][i]);
        rhs(yt,Kk[9]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A111*Kk[0][i]+A114*Kk[3][i]+A115*Kk[4][i]+A116*Kk[5][i]+A117*Kk[6][i]+A118*Kk[7][i]+A119*Kk[8][i]+A1110*Kk[9][i]);
        rhs(yt,Kk[10]);
        for(int i=0;i<18;i++) yt[i]=y[i]+hh*(A121*Kk[0][i]+A124*Kk[3][i]+A125*Kk[4][i]+A126*Kk[5][i]+A127*Kk[6][i]+A128*Kk[7][i]+A129*Kk[8][i]+A1210*Kk[9][i]+A1211*Kk[10][i]);
        rhs(yt,Kk[11]);
        for(int i=0;i<18;i++) ynew[i]=y[i]+hh*(B1*Kk[0][i]+B6*Kk[5][i]+B7*Kk[6][i]+B8*Kk[7][i]+B9*Kk[8][i]+B10*Kk[9][i]+B11*Kk[10][i]+B12*Kk[11][i]);
        /* 误差范数(scipy DOP853 _estimate_error_norm 同式) */
        double n5=0.0,n3=0.0;
        for(int i=0;i<18;i++){
          double sc=ATOL+RTOL*fmax(fabs(y[i]),fabs(ynew[i]));
          double e5=(E51*Kk[0][i]+E56*Kk[5][i]+E57*Kk[6][i]+E58*Kk[7][i]+E59*Kk[8][i]+E510*Kk[9][i]+E511*Kk[10][i]+E512*Kk[11][i])/sc;
          double e3=(E31*Kk[0][i]+E36*Kk[5][i]+E37*Kk[6][i]+E38*Kk[7][i]+E39*Kk[8][i]+E310*Kk[9][i]+E311*Kk[10][i]+E312*Kk[11][i])/sc;
          n5+=e5*e5; n3+=e3*e3;
        }
        double enorm;
        if(n5==0.0&&n3==0.0) enorm=0.0;
        else { double den=n5+0.01*n3; enorm=fabs(hh)*n5/sqrt(den*18.0); }
        if(enorm<1.0){
          double factor;
          if(enorm==0.0) factor=MAX_FACTOR; else factor=SAFETY*pow(enorm,-0.125);
          if(factor>MAX_FACTOR) factor=MAX_FACTOR;
          t+=hh;
          for(int i=0;i<18;i++) y[i]=ynew[i];
          h=hh*factor; if(h>1.0) h=1.0;
        } else {
          double factor=SAFETY*pow(enorm,-0.125);
          if(factor<MIN_FACTOR) factor=MIN_FACTOR;
          h=hh*factor;
        }
        if(h<1e-13){ fprintf(stderr,"step underflow t=%.17g\n",t); fclose(f); return 2; }
      }
      double rex=y[6]-y[3],rey=y[7]-y[4],rez=y[8]-y[5];
      double rem=sqrt(rex*rex+rey*rey+rez*rez);
      if(rem<rmin) rmin=rem;
    }
    if(rmin<gmin){gmin=rmin;g_orb=orb;}
    fprintf(f,"%s%.17g",orb?",":"",rmin);
  }
  fclose(f);
  FILE*f2=fopen(outp,"a");
  fprintf(f2,"],\"floor_min\":%.17g,\"orb_of_min\":%d,\"floor_over_a\":%.17g,\"nfev\":%ld,\"stack\":\"lgt-C-DOP853-v1\"}\n",gmin,g_orb,gmin/0.00256956,NFEV);
  fclose(f2);
  return 0;
}
