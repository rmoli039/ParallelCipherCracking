import pycuda.autoinit
from pycuda.compiler import SourceModule
import pycuda.driver as cuda
import time
import numpy
import random
import string
from itertools import product

original_string = "THE ONE STRING"
message = "THE PNE SURINH"
key_used = "AAAB"

b = numpy.array("the one string")
vignere_key = numpy.array(list(product(list(string.ascii_uppercase),repeat=4)))
encrypted_message = numpy.repeat([message],len(vignere_key))
key_len = numpy.array(4).astype(numpy.int32)
str_len = numpy.array(len(message)).astype(numpy.int32)

em_gpu = cuda.mem_alloc(2*encrypted_message.nbytes)
b_gpu = cuda.mem_alloc(b.nbytes)
key_gpu = cuda.mem_alloc(vignere_key.nbytes)
keylen_gpu = cuda.mem_alloc(key_len.nbytes)
strlen_gpu = cuda.mem_alloc(str_len.nbytes)

cuda.memcpy_htod(em_gpu, encrypted_message)
cuda.memcpy_htod(b_gpu, b)
cuda.memcpy_htod(key_gpu, vignere_key)
cuda.memcpy_htod(keylen_gpu, key_len)
cuda.memcpy_htod(strlen_gpu, str_len)

print("Original String: " + str(original_string))
print("Encrypted String: " + str(message))
print("Key used: " + str(key_used))

mod = SourceModule("""

    __global__ void convert(char *c, char *answer, char *key, int *keyLen, int *strLen)
    {
        int keyLength = keyLen[0];
        int strLength = strLen[0];
        int iterator;

        for(iterator = 0; iterator < 92; ++iterator)
        {
            long blockId = blockIdx.x + (4992 * iterator);
            long idx = (blockId * blockDim.x) + threadIdx.x;
            int i, j;
            char *newKeys = new char[strLength];

            for(i = 0, j = 0; i < strLength; ++i, ++j)
            {
                if (j == keyLength)
                    j = 0; 
                
                if (c[i] == 32)
                {  
                    j--;
                } 
                else
                {
                    newKeys[i] = key[j + (4 * ((blockId * blockDim.x) / strLength))];
                } 
            }
            
            if (c[idx] == 32) {}
            else
            {
                c[idx] = (c[idx] - newKeys[idx % (blockDim.x)] + 26) % 26;
                c[idx] = c[idx] < 0 ? c[idx] + 26 : c[idx];
                c[idx] += 'A';
            }

            delete[] newKeys;
        }
    }

""")

convert = mod.get_function("convert")
start = time.time()
convert(em_gpu,b_gpu,key_gpu,keylen_gpu,strlen_gpu,block=(len(message),1,1),grid=(4992,1))

em_decrypted = numpy.empty_like(encrypted_message)
cuda.memcpy_dtoh(em_decrypted,em_gpu)
end = time.time()
print(em_decrypted)

# This function generates the  
# key in a cyclic manner until  
# it's length isn't equal to  
# the length of original text 
def generateKey(string, key): 
    key = list(key) 
    if len(string) == len(key): 
        return(key) 
    else: 
        for i in range(len(string) - 
                       len(key)): 
            key.append(key[i % len(key)]) 
    return("" . join(key)) 

# This function decrypts the  
# encrypted text and returns  
# the original text 
def originalText(cipher_text, key): 
    orig_text = [] 
    for i in range(len(cipher_text)): 
        x = (ord(cipher_text[i]) - 
             ord(key[i]) + 26) % 26
        x += ord('A') 
        orig_text.append(chr(x)) 
    return("" . join(orig_text)) 
      
seq_start = time.time()
# Driver code 
for potential_key in vignere_key:
    blank = originalText(message,generateKey(message,potential_key))
seq_end = time.time()

print("Sequential Run Time: " + str(seq_end - seq_start) + " s")
print("Parallel Run Time: "   + str(end - start) + " s") 
