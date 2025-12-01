I just can't pass Incorrectness | test_param_shadow_fail | Failed (0/1) even though I thought of all possible scenarios. For our test cases,

def main() {
  if (true) {
    bvar i;
    i = 5;
    var i;  /* This should work since different scope */
    print(i);
  }
}

/*
*OUT*
5
*OUT*
*/

We should allow this right? Also, local var can shadow captured names according to my understanding, and also bvar and var can be in the same block since they are in different scope according to the test standard output. Currently I only check for duplicates for (var: if the same name exist in env[-1][0] which includes my captured variables with values shadowed by lambda parameters) and (bvar: if the same exists in env[-1][-1]). This should allow proper shadowing while detecting duplicates. Somehow I just can't pass the test...