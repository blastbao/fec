import fec

import array

def encode_file(inf, cb, k, m, chunksize=4096):
    """
    Read in the contents of inf, encode, and call cb with the results.

    First, k "input shares" will be read from inf, each input share being of 
    size chunksize.  Then these k shares will be encoded into m "result 
    shares".  Then cb will be invoked, passing a list of the m result shares 
    as its first argument, and the length of the encoded data as its second 
    argument.  (The length of the encoded data is always equal to k*chunksize, 
    until the last iteration, when the end of the file has been reached and 
    less than k*chunksize bytes could be read from the file.)  This procedure 
    is iterated until the end of the file is reached, in which case the space 
    of the input shares that is unused is filled with zeroes before encoding.

    Note that the sequence passed in calls to cb() contains mutable array
    objects in its first k elements whose contents will be overwritten when 
    the next segment is read from the input file.  Therefore the 
    implementation of cb() has to either be finished with those first k arrays 
    before returning, or if it wants to keep the contents of those arrays for 
    subsequent use after it has returned then it must make a copy of them to 
    keep.

    @param inf the file object from which to read the data
    @param cb the callback to be invoked with the results
    @param k the number of shares required to reconstruct the file
    @param m the total number of shares created
    @param chunksize how much data to read from inf for each of the k input 
        shares
    """
    enc = fec.Encoder(k, m)
    l = tuple([ array.array('c') for i in range(k) ])
    indatasize = k*chunksize # will be reset to shorter upon EOF
    ZEROES=array.array('c', ['\x00'])*chunksize
    while indatasize == k*chunksize:
        # This loop body executes once per segment.
        i = 0
        while (i<len(l)):
            # This loop body executes once per chunk.
            a = l[i]
            i += 1
            del a[:]
            try:
                a.fromfile(inf, chunksize)
            except EOFError:
                indatasize = i*chunksize + len(a)
                
                # padding
                a.fromstring("\x00" * (chunksize-len(a)))
                while (i<len(l)):
                    a[:] = ZEROES
                    i += 1

        # print "about to encode()... len(l[0]): %s, l[0]: %s" % (len(l[0]), type(l[0]),),
        res = enc.encode(l)
        # print "...finished to encode()"
        cb(res, indatasize)

def encode_file_stringy(inf, cb, k, m, chunksize=4096):
    """
    Read in the contents of inf, encode, and call cb with the results.

    First, k "input shares" will be read from inf, each input share being of 
    size chunksize.  Then these k shares will be encoded into m "result 
    shares".  Then cb will be invoked, passing a list of the m result shares 
    as its first argument, and the length of the encoded data as its second 
    argument.  (The length of the encoded data is always equal to k*chunksize, 
    until the last iteration, when the end of the file has been reached and 
    less than k*chunksize bytes could be read from the file.)  This procedure 
    is iterated until the end of the file is reached, in which case the space 
    of the input shares that is unused is filled with zeroes before encoding.

    @param inf the file object from which to read the data
    @param cb the callback to be invoked with the results
    @param k the number of shares required to reconstruct the file
    @param m the total number of shares created
    @param chunksize how much data to read from inf for each of the k input 
        shares
    """
    enc = fec.Encoder(k, m)
    indatasize = k*chunksize # will be reset to shorter upon EOF
    while indatasize == k*chunksize:
        # This loop body executes once per segment.
        i = 0
	l = []
        ZEROES = '\x00'*chunksize
        while i<k:
            # This loop body executes once per chunk.
            i += 1
            l.append(inf.read(chunksize))
            if len(l[-1]) < chunksize:
                indatasize = i*chunksize + len(l[-1])
                
                # padding
                l[-1] = l[-1] + "\x00" * (chunksize-len(l[-1]))
                while i<k:
                    l.append(ZEROES)
                    i += 1

        # print "about to encode()... len(l[0]): %s, l[0]: %s" % (len(l[0]), type(l[0]),),
        res = enc.encode(l)
        # print "...finished to encode()"
        cb(res, indatasize)

