#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <stdint.h>
#include <time.h>

#define MSR_TERM_STATUS 0x19c        // cpus temp
#define MSR_TEMPERATURE_TARGET 0x1a2 // for TjMax
#define PATH_MSR_FILE "/dev/cpu/%d/msr"
#define PRINT_USAGE   printf("Usage: \n(1) rdmsr for start program with default values              \
                      \n(2) rdmsr ExecutionTime-(opt) readMsrEveryNanoSecs-(opt)                    \
                      \n(3) rdmsr INF-(unbounded execution) readMsrEveryNanoSecs-(opt)\n            \
                      \n(4) rdmsr INF-(unbounded execution) readMsrEveryNanoSecs-(opt) cpu-(opt)"); \
                      exit(EXIT_FAILURE);
#define UNBOUNDED "INF"
#define DEFAULT_READ 100000000
#define DEFAULT_DURATION 5
#define READ_ALL_CPUS -1

int main(int argc, char **argv){
  int fd;
  uint64_t tj_max;
  uint64_t value;

  int n_cpus = sysconf(_SC_NPROCESSORS_ONLN);

  char msr_path[64];
  
  typedef enum {false, true} bool;
  bool unbounded = false;

  time_t duration_secs;   // time of program running
     
  struct timespec read_nanosecs;  // time every read occour
  read_nanosecs.tv_sec = 0;
  read_nanosecs.tv_nsec = 0;
  
  char *end;
  int rd_cpu = READ_ALL_CPUS;

  if(argv[1] != NULL){
    if(strcmp(argv[1],UNBOUNDED) == 0){
      unbounded = true;
    }else{

    duration_secs = strtol(argv[1], &end, 10);
    
    if(*end != '\0'){
      PRINT_USAGE
    }
  }
  }else{ // default value, run for 5 secs
    printf("Setting duration time to %d secs\n", DEFAULT_DURATION);
    duration_secs = DEFAULT_DURATION;
  }

  if(argc == 3 && argv[2] != NULL){
    end = NULL;
    read_nanosecs.tv_nsec = strtol(argv[2], &end, 10);
    if(*end != '\0'){
      PRINT_USAGE
    }
  }else{ // default value, reads msr every 1 ms
    printf("Setting reads of MSRs every %dns\n", DEFAULT_READ);
    read_nanosecs.tv_nsec = 50000000;
  }

  if(argc == 4 && argv[3] != NULL){
    end = NULL;
    rd_cpu = strtol(argv[3], &end, 10);
    if(*end != '\0'){
      PRINT_USAGE
    }
  }
  
  read_nanosecs.tv_nsec = 50000000;
  
  time_t start_time = time(NULL);

  if (rd_cpu != READ_ALL_CPUS){
    // read msr of single CPU
    sprintf(msr_path, PATH_MSR_FILE, rd_cpu);

    if ((fd = open(msr_path, O_RDONLY)) == -1){
      fprintf(stderr, "Error opening %s. Action not performed\n", msr_path);
      exit(EXIT_FAILURE);
    }

    while (unbounded || (time(NULL) - start_time < duration_secs)){
      if (pread(fd, &value, sizeof(value), MSR_TERM_STATUS) != sizeof(value)){
        fprintf(stderr, "CPU[%2d] - error reading MSR\n", rd_cpu);
      }
      nanosleep(&read_nanosecs, NULL);
    }

    close(fd);
    
  }else{
    int fd_arr[n_cpus];
    for (register int i = 0; i < n_cpus; i++){
      sprintf(msr_path, PATH_MSR_FILE, i);
      if ((fd_arr[i] = open(msr_path, O_RDONLY)) == -1){
        fprintf(stderr, "Error opening %s. Action not performed\n", msr_path);
        exit(EXIT_FAILURE);
      }
    }

    // read MRS on all CPUs
    while (unbounded || (time(NULL) - start_time < duration_secs)){
      for (register int i = 0; i < n_cpus; i++){
        if (pread(fd_arr[i], &value, sizeof(value), MSR_TERM_STATUS) != sizeof(value)){
          fprintf(stderr, "CPU[%2d] - error reading MSR\n", rd_cpu);
        }
      }
      nanosleep(&read_nanosecs, NULL);
    }

    for (register int i = 0; i < n_cpus; i++){
      close(fd_arr[i]);
    }

  }

  return EXIT_SUCCESS;
}