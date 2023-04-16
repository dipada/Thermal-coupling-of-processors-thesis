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
#define PRINT_USAGE fprintf(stderr, "Usage: %s [ -U | -e secs ] [ -r nanosecs ] [ -c ncpu ]             \
                                                \n-U unbounded execution                                \
                                                \n-e execution time                                     \
                                                \n-r reads frequency                                    \
                                                \n-c cpu for msr reads\n", argv[0]); exit(EXIT_FAILURE);
#define UNBOUNDED "INF"
#define DEFAULT_READ_NS 100000000  // 100ms default read msr
#define DEFAULT_DURATION 5
#define NANOSEC_LIMIT 999999999
#define READ_ALL_CPUS -1

extern char *optarg;
extern int optind;

int main(int argc, char **argv){
  int fd;
  uint64_t tj_max;
  uint64_t value;

  int n_cpus = sysconf(_SC_NPROCESSORS_ONLN);

  char msr_path[64];
  
  typedef enum {false, true} bool;
  bool unbounded = false;
  bool user_duration = false;

  time_t duration_secs;   // time of program running
     
  struct timespec read_nanosecs;  // time every read occour
  read_nanosecs.tv_sec = 0;
  read_nanosecs.tv_nsec = DEFAULT_READ_NS;
  
  char *end;
  int rd_cpu = READ_ALL_CPUS;

  int opt;

  while ((opt = getopt(argc, argv, "Ue:r:c:")) != -1){
    
    switch (opt){
      case 'U': // unbounded execution
        unbounded = true;
        printf("Unbounded execution\n");
        break;

      case 'e': // user defined execution time
        duration_secs = strtol(optarg, &end, 10);
        if(*end != '\0'){
          PRINT_USAGE
        }
        
        user_duration = true;

        printf("Execution time: %ld secs\n", duration_secs);
        break;

      case 'r': // user defined read msr time
        long nanosecs = strtol(optarg, &end, 10);
        if(*end != '\0'){
          PRINT_USAGE
        }
        while (nanosecs > NANOSEC_LIMIT){
          read_nanosecs.tv_sec += 1;
          nanosecs -= NANOSEC_LIMIT;
        }
        read_nanosecs.tv_nsec = nanosecs;      

        printf("Read msr every %ld secs and %ld nanosecs\n", read_nanosecs.tv_sec, read_nanosecs.tv_nsec);
        break;

      case 'c': // user defined cpu to read msr
        rd_cpu = strtol(optarg, &end, 10);
        if(*end != '\0'){
          PRINT_USAGE
        }
        printf("Read msr of CPU %d\n", rd_cpu);
        break;

      default: /* '?' */
        PRINT_USAGE
    }
  }

  if (optind < argc){
    PRINT_USAGE
  }

  if (user_duration && unbounded){
    printf("Can't set unbounded execution and time for execution at the same time\n");
    PRINT_USAGE
  }
  
  
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