# Modified by SignalFx
#
# Autogenerated by Thrift Compiler (0.9.3)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:new_style
#
import six
from six.moves import xrange

from thrift.Thrift import TType, TMessageType, TException, TApplicationException
import logging
from .ttypes import *
from thrift.Thrift import TProcessor
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class Iface(object):
  def emitZipkinBatch(self, spans):
    """
    Parameters:
     - spans
    """
    pass

  def emitBatch(self, batch):
    """
    Parameters:
     - batch
    """
    pass


class Client(Iface):
  def __init__(self, iprot, oprot=None):
    self._iprot = self._oprot = iprot
    if oprot is not None:
      self._oprot = oprot
    self._seqid = 0

  def emitZipkinBatch(self, spans):
    """
    Parameters:
     - spans
    """
    self.send_emitZipkinBatch(spans)

  def send_emitZipkinBatch(self, spans):
    self._oprot.writeMessageBegin('emitZipkinBatch', TMessageType.ONEWAY, self._seqid)
    args = emitZipkinBatch_args()
    args.spans = spans
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()
  def emitBatch(self, batch):
    """
    Parameters:
     - batch
    """
    self.send_emitBatch(batch)

  def send_emitBatch(self, batch):
    self._oprot.writeMessageBegin('emitBatch', TMessageType.ONEWAY, self._seqid)
    args = emitBatch_args()
    args.batch = batch
    args.write(self._oprot)
    self._oprot.writeMessageEnd()
    self._oprot.trans.flush()

class Processor(Iface, TProcessor):
  def __init__(self, handler):
    self._handler = handler
    self._processMap = {}
    self._processMap["emitZipkinBatch"] = Processor.process_emitZipkinBatch
    self._processMap["emitBatch"] = Processor.process_emitBatch

  def process(self, iprot, oprot):
    (name, type, seqid) = iprot.readMessageBegin()
    if name not in self._processMap:
      iprot.skip(TType.STRUCT)
      iprot.readMessageEnd()
      x = TApplicationException(TApplicationException.UNKNOWN_METHOD, 'Unknown function %s' % (name))
      oprot.writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
      x.write(oprot)
      oprot.writeMessageEnd()
      oprot.trans.flush()
      return
    else:
      self._processMap[name](self, seqid, iprot, oprot)
    return True

  def process_emitZipkinBatch(self, seqid, iprot, oprot):
    args = emitZipkinBatch_args()
    args.read(iprot)
    iprot.readMessageEnd()
    try:
      self._handler.emitZipkinBatch(args.spans)
      msg_type = TMessageType.REPLY
    except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
      raise
    except:
      pass

  def process_emitBatch(self, seqid, iprot, oprot):
    args = emitBatch_args()
    args.read(iprot)
    iprot.readMessageEnd()
    try:
      self._handler.emitBatch(args.batch)
      msg_type = TMessageType.REPLY
    except (TTransport.TTransportException, KeyboardInterrupt, SystemExit):
      raise
    except:
      pass


# HELPER FUNCTIONS AND STRUCTURES

class emitZipkinBatch_args(object):
  """
  Attributes:
   - spans
  """

  thrift_spec = (
    None, # 0
    (1, TType.LIST, 'spans', (TType.STRUCT,(zipkincore.ttypes.Span, zipkincore.ttypes.Span.thrift_spec)), None, ), # 1
  )

  def __init__(self, spans=None,):
    self.spans = spans

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.LIST:
          self.spans = []
          (_etype3, _size0) = iprot.readListBegin()
          for _i4 in xrange(_size0):
            _elem5 = zipkincore.ttypes.Span()
            _elem5.read(iprot)
            self.spans.append(_elem5)
          iprot.readListEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('emitZipkinBatch_args')
    if self.spans is not None:
      oprot.writeFieldBegin('spans', TType.LIST, 1)
      oprot.writeListBegin(TType.STRUCT, len(self.spans))
      for iter6 in self.spans:
        iter6.write(oprot)
      oprot.writeListEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.spans)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in six.iteritems(self.__dict__)]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class emitBatch_args(object):
  """
  Attributes:
   - batch
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'batch', (jaeger.ttypes.Batch, jaeger.ttypes.Batch.thrift_spec), None, ), # 1
  )

  def __init__(self, batch=None,):
    self.batch = batch

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.batch = jaeger.ttypes.Batch()
          self.batch.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('emitBatch_args')
    if self.batch is not None:
      oprot.writeFieldBegin('batch', TType.STRUCT, 1)
      self.batch.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.batch)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in six.iteritems(self.__dict__)]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)