'''
Student Name: Liyao Jiang
Student ID: 1512445
Section: EB1
Student Name: Xiaolei Zhang
Student ID: 1515335
Section: B1
Cmput 275 Assignment2
Huffman Coding
'''

# The functions in this file are to be implemented by students.

import bitio
import huffman


def read_tree(bitreader):
	'''Read a description of a Huffman tree from the given bit reader,
	and construct and return the tree. When this function returns, the
	bit reader should be ready to read the next bit immediately
	following the tree description.

	Huffman trees are stored in the following format:
	  * TreeLeaf is represented by the two bits 01, followed by 8 bits
		  for the symbol at that leaf.
	  * TreeLeaf that is None (the special "end of message" character) 
		  is represented by the two bits 00.
	  * TreeBranch is represented by the single bit 1, followed by a
		  description of the left subtree and then the right subtree.

	Args:
	  bitreader: An instance of bitio.BitReader to read the tree from.

	Returns:
	  A Huffman tree constructed according to the given description.
	'''

	# a recursive reader (helper function)
	def recurse_read(bitreader, huffman_tree=None):
		# read the first bit
		bit_read = bitreader.readbit()

		# if the first bit is 1, it is a TreeBranch
		if bit_read == 1:
			left_leaf = recurse_read(bitreader)
			right_leaf = recurse_read(bitreader)
			huffman_tree = huffman.TreeBranch(left_leaf,right_leaf)
			return huffman_tree

		# there is two cases when the first bit is 0
		elif bit_read == 0:
			bit_read = bitreader.readbit()

			# case of a none TreeLeaf
			if bit_read == 0:
				leaf = huffman.TreeLeaf(None)
			# case of a normal TreeLeaf
			elif bit_read == 1:
				# use bitreader to get value from the following byte
				byte_read = bitreader.readbits(8)
				leaf = huffman.TreeLeaf(byte_read)
			return leaf

	# call the helper
	huffman_tree = recurse_read(bitreader)

	return huffman_tree


def decode_byte(tree, bitreader):
	"""
	Reads bits from the bit reader and traverses the tree from
	the root to a leaf. Once a leaf is reached, bits are no longer read
	and the value of that leave is returned.
	
	Args:
	  bitreader: An instance of bitio.BitReader to read the tree from.
	  tree: A Huffman tree.

	Returns:
	  Next byte of the compressed bit stream.
	"""
	while True:
		# traverses the tree until a leaf is reached
		if isinstance(tree, huffman.TreeBranch):
			# set the next tree to the left or right subtree
			if bitreader.readbit() == 0:
				tree = tree.left
			else:
				tree = tree.right
		# now we reached a TreeLeaf, simply return its value
		# if the value is None, we will actually return None
		elif isinstance(tree, huffman.TreeLeaf):
			return tree.value


def decompress(compressed, uncompressed):
	'''First, read a Huffman tree from the 'compressed' stream using your
	read_tree function. Then use that tree to decode the rest of the
	stream and write the resulting symbols to the 'uncompressed'
	stream.

	Args:
	  compressed: A file stream from which compressed input is read.
	  uncompressed: A writable file stream to which the uncompressed
		  output is written.

	'''

	# instances of the BitReader and BitWriter
	reader = bitio.BitReader(compressed)
	writer = bitio.BitWriter(uncompressed)

	# first read the huffman tree off the compressed file
	huffman_tree = read_tree(reader)
	# continue to read the bytes encoded using tree 
	while True:
		# decode the next byte
		byte_read = decode_byte(huffman_tree,reader)
		# stop when end-of-message is read
		if byte_read == None:
			break
		# write the byte to the uncompressed file
		writer.writebits(byte_read,8)


def write_tree(tree, bitwriter):
	'''Write the specified Huffman tree to the given bit writer.  The
	tree is written in the format described above for the read_tree
	function.

	DO NOT flush the bit writer after writing the tree.

	Args:
	  tree: A Huffman tree.
	  bitwriter: An instance of bitio.BitWriter to write the tree to.
	'''
	# write the tree recursively
	# call write_tree itself, for both of the left and right child
	if isinstance(tree, huffman.TreeBranch):
		bitwriter.writebit(1)
		write_tree(tree.left, bitwriter)
		write_tree(tree.right, bitwriter)
	# two cases for TreeLeaf
	elif isinstance(tree, huffman.TreeLeaf):
		bitwriter.writebit(0)
		if tree.value == None:
			bitwriter.writebit(0) # wrtie 00(None Treeleaf)
		else:
			bitwriter.writebit(1)
			bitwriter.writebits(tree.value, 8) # write the value of Leaf


def compress(tree, uncompressed, compressed):
	'''First write the given tree to the stream 'compressed' using the
	write_tree function. Then use the same tree to encode the data
	from the input stream 'uncompressed' and write it to 'compressed'.
	If there are any partially-written bytes remaining at the end,
	write 0 bits to form a complete byte.

	Flush the bitwriter after writing the entire compressed file.

	Args:
	  tree: A Huffman tree.
	  uncompressed: A file stream from which you can read the input.
	  compressed: A file stream that will receive the tree description
		  and the coded input data.
	'''

	# instances of the BitReader and BitWriter
	reader = bitio.BitReader(uncompressed)
	writer = bitio.BitWriter(compressed)

	# make the encoding table for the given tree
	encode_table = huffman.make_encoding_table(tree)

	# call write_tree, to write the tree to the compressed file
	write_tree(tree,writer)

	# write all the bytes untill EOFError occurs
	while True:
		try:
			# read the byte from uncompressed file
			byte_towrite = reader.readbits(8)
			# encode the byte using the dictionary
			bit_sequence = encode_table[byte_towrite]
			# write each bit to the compressed file
			for b in bit_sequence:
				if b == True:
					writer.writebit(1)
				elif b == False:
					writer.writebit(0)

		except EOFError:
			bit_sequence = encode_table[None]
			# write each bit to the compressed file
			for b in bit_sequence:
				if b == True:
					writer.writebit(1)
				elif b == False:
					writer.writebit(0)
			# stop the loop
			break
	# Flush the bitwriter
	writer.flush()


