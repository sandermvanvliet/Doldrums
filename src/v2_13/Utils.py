import math

import v2_13.Constants as Constants

class NumericUtils:
	def roundDown(n, m):
		return n - n % m

	def roundUp(n, m):
		return (n - 1) + m - (n - 1) % m

class StreamUtils:
	kDataBitsPerByte = 7
	kByteMask = (1 << kDataBitsPerByte) - 1 # 0x0fffffff
	kMaxUnsignedDataPerByte = kByteMask # 0x0fffffff
	kMinDataPerByte = -(1 << (kDataBitsPerByte - 1))
	kMaxDataPerByte = (~kMinDataPerByte & kByteMask) # 0x3f
	kEndByteMarker = (255 - kMaxDataPerByte) # 0xc0
	kEndUnsignedByteMarker = (255 - kMaxUnsignedDataPerByte) # 0x10000000

	#FIXME: find a not so hacky way of reading only one byte
	def read(stream, endByteMarker, maxLoops = -1):
		b = int.from_bytes(stream.read(1), 'big', signed=False)
		r = 0
		s = 0
		while (b <= StreamUtils.kMaxUnsignedDataPerByte):
			r |= b << s
			s += StreamUtils.kDataBitsPerByte
			x = stream.read(1)
			b = int.from_bytes(x, 'big', signed=False)
			maxLoops -= 1

		return r | ((b - endByteMarker) << s)

	# 7 data bits per byte because of marker
	def readUnsigned(stream, size = -7):
		if size == 8:
			return int.from_bytes(stream.read(1), 'big', signed=False) # No marker
		return StreamUtils.read(stream, StreamUtils.kEndUnsignedByteMarker, math.ceil(size / 7))

	def readInt(stream, size):
		if size == 8:
			return int.from_bytes(stream.read(1), 'big', signed=True) # No marker
		return StreamUtils.read(stream, StreamUtils.kEndByteMarker, math.ceil(size / 7))

	def readCid(stream):
		return StreamUtils.readInt(stream, 32)

	def readRef(stream):
		return StreamUtils.readUnsigned(stream)

	def readTokenPosition(stream):
		return StreamUtils.readInt(stream, 32)

	def readBool(stream):
		b = stream.read(1)
		if b == b'\x00':
			return False
		elif b == b'\x01':
			return True
		else:
			raise Exception('Expected boolean, but received non-boolean value while reading at stream offset: ' + str(stream.tell()))

	def readString(stream):
		res = b''
		b = stream.read(1)
		while b != b'\x00':
			res += b
			b = stream.read(1)
		return res

	def readWordWith32BitReads(stream):
		value = 0
		for j in range(Constants.kNumRead32PerWord):
			partialValue = StreamUtils.readUnsigned(stream, 32)
			value |= partialValue << (j * 32)
		return value

class DecodeUtils:
	def decodeStaticBit(value):
		r = (value >> 1) & 1
		if r == 0:
			return False
		elif r == 1:
			return True
		else:
			raise Exception('Encountered non-boolean expression')

	def decodeTypeBits(value):
		return value & 0x7f

def isTopLevelCid(cid):
	return cid >= Constants.kTopLevelCidOffset

def getVersionInfo(hsh):
	if hsh == '8ee4ef7a67df9845fba331734198a953':
		return 'Dart v2.10'
	else:
		return 'unknown version'