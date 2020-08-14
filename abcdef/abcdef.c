#include <stdio.h>
#include <stdlib.h>
#include "common.h"
#include <unistd.h> 
// sleep(1s)

#define N 10*1024*1024

struct DATAa {
    int a;
    int b;
    int c;
    int d;
};
struct DATAb {
    int a;
    int b;
};




int maina() {
    int i;
    struct DATAa* p = (struct DATAa*) malloc(sizeof(struct DATAa) * N);
    uint64_t start, stop;

    start = rte_rdtsc();
    for(i=0; i<N; i++) {
        p[i].a = p[i].b;
    }
    stop = rte_rdtsc();

    printf(FMT64 "\n", stop - start);

    return 0;
}




int mainb() {
    int i;
    struct DATAb* p = (struct DATAb*) malloc(sizeof(struct DATAb) * N);
    uint64_t start, stop;

    start = rte_rdtsc();
    for(i=0; i<N; i++) {
        p[i].a = p[i].b;
    }
    stop = rte_rdtsc();

    printf(FMT64 "\n", stop - start);

    return 0;
}

#define Nc 36*1024*1024

struct DATAc {
    char a;
    int b;
    char c;
};

int mainc(void) {
    int i;
    struct DATAc* p = (struct DATAc*) malloc(sizeof(struct DATAc) * Nc);
    uint64_t start, stop;

    start = rte_rdtsc();
    for(i=0; i<Nc; i++) {
        p[i].a++;
    }
    stop = rte_rdtsc();

    printf(FMT64 "\n", stop - start);

    return 0;
}


#define Nd 36*1024*1024

struct DATAd {
    int b;
    char a;
    char c;
};

int maind(void) {
    int i;
    struct DATAd* p = (struct DATAd*) malloc(sizeof(struct DATAd) * Nd);
    uint64_t start, stop;

    start = rte_rdtsc();
    for(i=0; i<Nd; i++) {
        p[i].a++;
    }
    stop = rte_rdtsc();

    printf(FMT64 "\n", stop - start);

    return 0;
}


#define Ne   10*1024*1024
#define ROWe 1024
#define COLe 10*1024

int maine(void) {
    int i, j;
    int* p = (int*) malloc(sizeof(int) * Ne);
    uint64_t start, stop;

    start = rte_rdtsc();
    for(i=0; i<COLe; i++) {
        for(j=0; j<ROWe; j++) {
            p[i + j*COLe] ++;
        }
    }
    stop = rte_rdtsc();

    printf(FMT64 "\n", stop - start);

    return 0;
}

#define Nf   10*1024*1024
#define ROWf 1024
#define COLf 10*1024

int mainf(void) {
    int i, j;
    int* p = (int*) malloc(sizeof(int) * Nf);
    uint64_t start, stop;

    start = rte_rdtsc();
    for(j=0; j<ROWf; j++) {
        for(i=0; i<COLf; i++) {
            p[i + j*COLf] ++;
        }
    }
    stop = rte_rdtsc();

    printf(FMT64 "\n", stop - start);

    return 0;
}







int main(void) {
	sleep(1);
	maina();
	sleep(1);
	mainb();
	sleep(1);
	mainc();
	sleep(1);
	maind();
	sleep(1);
	maine();
	sleep(1);
	mainf();
	sleep(1);
    return 0;
}
