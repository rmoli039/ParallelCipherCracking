import pycuda.autoinit
from pycuda.compiler import SourceModule
import pycuda.driver as cuda
import time
import numpy
import random

key = random.randint(1,26)

original_string = "The One String"
message = "Aol Vul Zaypun"
key_used = "7"

print("Original String: " + str(original_string))
print("Encrypted String: " + str(message))
print("Key used: " + str(key_used))

EncryptedMessage = ""

for line in original_string:
    EncryptedChar = ord(line) + key
    EncryptedMessage += chr(EncryptedChar)

DecryptedMessage = ""

for line in EncryptedMessage:
    DecryptedChar = ord(line) - key
    DecryptedMessage += chr(DecryptedChar)

#attempt to brute force Ceasar Cipher
sequentialStartTime = time.time()
bruteForceMessage = EncryptedMessage
bruteForceDecryptedMessage = ""
bruteForceKey = 0

attempt_count = 0

 
while bruteForceDecryptedMessage != DecryptedMessage:
    bruteForceKey += 1
    bruteForceDecryptedMessage = ""
    attempt_count += 1
    for line in bruteForceMessage:
        bruteForceEncryptedChar = ord(line) - bruteForceKey
        bruteForceDecryptedMessage += chr(bruteForceEncryptedChar)

sequentialEndTime = time.time()

sequentialRunTime = (sequentialEndTime - sequentialStartTime)
 

a = numpy.repeat(["Aol Vul Zaypun"],25)
b = numpy.array("The One String")
ceasarKey = numpy.arange(1,26).astype(numpy.int32)
out = numpy.zeros(26).astype(numpy.int32)

a_gpu = cuda.mem_alloc(a.nbytes)
b_gpu = cuda.mem_alloc(b.nbytes)
key_gpu = cuda.mem_alloc(ceasarKey.nbytes)
out_gpu = cuda.mem_alloc(out.nbytes)

cuda.memcpy_htod(a_gpu, a)
cuda.memcpy_htod(b_gpu, b)
cuda.memcpy_htod(key_gpu, ceasarKey)
cuda.memcpy_htod(out_gpu, out)

mod = SourceModule("""

    __global__ void convert(char *c, char *answer, int *key, int *out)
    {
     	if (key[blockIdx.x] == (7 + 1))
        {
            out[blockIdx.x - 1] = 1;
        }

	int idx = (blockIdx.x * blockDim.x) + threadIdx.x;

        if (c[idx] == 32) {}
        else if ((c[idx] - key[blockIdx.x]) < 65)
        {
            c[idx] = (c[idx] - key[blockIdx.x] - 65) % 26;
            c[idx] = c[idx] < 0 ? c[idx] + 26 : c[idx];
            c[idx] += 65;
        }
	else if ((c[idx] - key[blockIdx.x]) < 97 && c[idx] >= 97)
        {
            c[idx] = (c[idx] - key[blockIdx.x] - 97) % 26;
            c[idx] = c[idx] < 0 ? c[idx] + 26 : c[idx];
            c[idx] += 97;
        }
	else
	{
            c[idx] = c[idx] - key[blockIdx.x];
        }
    }

""")

convert = mod.get_function("convert")
startTime = time.time()
convert(a_gpu,b_gpu,key_gpu,out_gpu,block=(14,1,1),grid=(26,1))

a_decrypted = numpy.empty_like(a)
output = numpy.empty_like(out)
cuda.memcpy_dtoh(a_decrypted,a_gpu)
cuda.memcpy_dtoh(output,out_gpu)
print(a_decrypted)
print(output)
endTime = time.time()


totalTime = endTime - startTime
print("Sequential Run Time: " + str(sequentialRunTime) +" s")
print("Parallel Run Time: " + str(totalTime) + " s")
