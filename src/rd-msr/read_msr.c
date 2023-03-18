#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <stdint.h>
#include <time.h>
#include <ctype.h>

#define MSR_TERM_STATUS 0x19c        // cpus temp
#define MSR_TEMPERATURE_TARGET 0x1a2 // for TjMax
#define PATH_MSR_FILE "/dev/cpu/%d/msr"
#define PRINT_USAGE   printf("Usage: \n(1) rdmsr for start program with default values      \
                      \n(2) rdmsr ExecutionTime-(opt) readMsrEveryNanoSecs-(opt)            \
                      \n(3) rdmsr INF-(unbounded execution) readMsrEveryNanoSecs-(opt)\n"); \
                      exit(EXIT_FAILURE);
#define UNBOUNDED "INF"
#define DEFAULT_READ 1000000
#define DEFAULT_DURATION 5

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
    printf("Setting duration time to 5 secs\n");
    duration_secs = DEFAULT_DURATION;
  }

  if(argc == 3 && argv[2] != NULL){
    end = NULL;
    read_nanosecs.tv_nsec = strtol(argv[2], &end, 10);
    printf("2-end %c\n", *end);
    if(*end != '\0'){
      PRINT_USAGE
    }
  }else{ // default value, reads msr every 1 ms
    printf("Setting reads of MSRs every %dns\n", DEFAULT_READ);
    read_nanosecs.tv_nsec = DEFAULT_READ;
  }  
  
  
  time_t start_time = time(NULL);

  while (unbounded || (time(NULL) - start_time < duration_secs)){
    
    // Read MSRs of all CPUs
    for (register int i = 0; i < n_cpus; i++){
      sprintf(msr_path, PATH_MSR_FILE, i);
      printf("[%2d] -- msr_path %s ", i, msr_path);

      // read MSR of specific CPU
      fd = open(msr_path, O_RDONLY);
      if (fd < 0){
        fprintf(stderr, "Error opening %s. Action not performed\n", msr_path);
      }else{
        if (pread(fd, &value, sizeof(value), MSR_TERM_STATUS) != sizeof(value)){
          fprintf(stderr, "CPU[%2d] - error reading MSR\n", i);
        }else{
          printf("CPU[%2d] - 0x%lx\n", i, value >> 16 & 0x7F);
        }      
      }
      close(fd);
      
    }
    fflush(stdout);
    fflush(stderr);
    nanosleep(&read_nanosecs, NULL);
  }


  return EXIT_SUCCESS;
}