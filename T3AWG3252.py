import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set,strict_range,joined_validators
from pyvisa.errors import VisaIOError

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class T3AWG3252(Instrument):
    """ Represents the Teledyne T3AWG3252 Arbitrary Wave Generator
    
    .. code-block:: python
    """
    
    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "Teledyne T3AWG3252 Arbitrary Wave Generator", **kwargs)
    
    def run(self):
        self.write('AWGControl:RUN')
        return self.ask("*OPC?").strip()
    
    def stop(self):
        self.write('AWGControl:STOP')
        return self.ask("*OPC?").strip()
    
    def state(self):
        """
        0 indicates that the AWG has stopped.
        1 indicates that the AWG is waiting for trigger.
        2 indicates that the AWG is running.
        """
        return self.ask('AWGControl:RSTATe?')
    
    def idn(self):
        return self.ask('*IDN?')
    
    def trigger(self):
        self.write('*TRG')
        return self.ask("*OPC?").strip()
        
    def upload_waveform(self, arb_name, data_samples=None, folder=None):
        """
        Uploads an arbitrary trace into the volatile memory of the device.
        The data_samples must be given as a float signed list.
        """
        #Steps:
        #1) Format data samples
        if data_samples is None: # Generate default data samples (square signal)
            data_samples = np.repeat(np.tile([0,1]),10)
        data_samples = '\r\n'.join([str(i) for i in data_samples])
            
        if folder == None:
            folder = "C:/Users/awg3000/Pictures/Saved Pictures/"
        len_data = str(len(data_samples))
        
        #2) Transfer the text file from the PC to the mass storage device attached to the AWG
        self.stop()
        self.write('MMEMory:DOWNload:FNAMe "{}{}.txt"'.format(folder,arb_name))
        self.write('MMEMory:DOWNload:DATA #{}{}{}'.format(len(len_data),len_data,data_samples))
        self.ask("*OPC?").strip()
        #3) Import the waveform list
        self.write('WLISt:WAVeform:DELete "{0}"'.format(arb_name))
        self.write('WLISt:WAVeform:IMPort "{1}","{0}/{1}.txt",ANAlog'.format(folder,arb_name))
        return self.ask("*OPC?").strip()
    
    # System properties
    run_mode = Instrument.control(
        "AWGControl:RMODe?","AWGControl:RMODe %s",
        docs="""
        CONTinuous: each waveform will loop as written in the entry
        repetition parameter and the entire sequence is repeated
        circularly
                
        BURSt: the AWG waits for a trigger event. When the trigger
        event occurs each waveform will loop as written in the entry
        repetition parameter and the entire sequence will be
        repeated circularly many times as written in the Burst Count[N]
        parameter. If you set Burst Count[N]=1 the instrument is in
        Single mode and the sequence will be repeated only once.
                
        TCONtinuous: the AWG waits for a trigger event. When the
        trigger event occurs each waveform will loop as written in the
        entry repetition parameter and the entire sequence will be
        repeated circularly.
                
        STEPped: the AWG, for each entry, waits for a trigger event
        before the execution of the sequencer entry. The waveform
        of the entry will loop as written in the entry repetition
        parameter. After the generation of an entry has completed,
        the last sample of the current entry or the first sample of the
        next entry is held until the next trigger is received. At the end
        of the entire sequence the execution will restart from the first
        entry.
                
        ADVAnced: it enables the “Advanced” mode. In this mode
        the execution of the sequence can be changed by using
        conditional and unconditional jumps (JUMPTO and GOTO
        commands) and dynamic jumps (PATTERN JUMP commands).
        """,
        validator=strict_discrete_set,
        values=["CONT", "BURS", "TCON", "STEP", "ADVA"]
    )
    arb_srate=Instrument.control(
        "AWGControl:SRATe?", "AWGControl:SRATe %f",
        docs="""
        This command sets or returns the sample rate for the Sampling Clock.
        """,
    )
    
    display_unit_volt=Instrument.setting(
        "DISPlay:UNIT:VOLT %s",
        docs="""
        Selects the method for specifying voltage ranges. You can specify a
        voltage range as an amplitude and an offset or as high and low
        values.
        """,
        validator = strict_discrete_set,
        values = ["AMPL","HIGH"]
    )
        
    output_chn1 = Instrument.control(
        get_command="OUTPut1:STATe?",
        set_command="OUTPut1:STATe %s",
        docs=""" A boolean property that turns on (True, 'on') or off (False, 'off')
        the output of the function generator. Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ON', 'on': 'ON', 'ON' : 'ON', 1: 'ON',
                False: 'OFF', 'off': 'OFF', 'OFF': 'OFF', 0: 'OFF'}
    )
    
    output_load_chn1 = Instrument.control(
        "OUTPut1:SERIESIMPedance?", "OUTPut1:SERIESIMPedance %s",
        """ Sets the expected load resistance (should be the load impedance connected
        to the output. The output impedance is always 50 Ohm, this setting can be used
        to correct the displayed voltage for loads unmatched to 50 Ohm.
        Valid values are 50Ohm or 5Ohm.
        No validator is used since both numeric and string inputs are accepted,
        thus a value outside the range will not return an error.
        Can be set. """,
        validator=strict_discrete_set,
        values=['50Ohm','LOW']
    )
    
    voltage_high_chn1 = Instrument.control(
        "SEQuence:ELEM1:VOLTage:HIGH1?", "SEQuence:ELEM1:VOLTage:HIGH1 %s",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -3 V to 3 V (must be higher than low
        voltage by at least 1 mV). Can be set. """,
        validator=strict_range,
        values=[-3, 3],
    )
    
    voltage_low_chn1 = Instrument.control(
        "SEQuence:ELEM1:VOLTage:LOW1?", "SEQuence:ELEM1:VOLTage:LOW1 %s",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -3 V to 3 V (must be higher than low
        voltage by at least 1 mV). Can be set. """,
        validator=strict_range,
        values=[-3, 3],
    )
    
    amplitude_chn1 = Instrument.control(
        "SEQuence:ELEM1:AMPlitude1?", "SEQuence:ELEM1:AMPlitude1 %s",
        """ Sets or returns the voltage peak-to-peak amplitude for the element
        “n=1” of the channel “m=1”.
        
        Apart from the amplitude in volts it can also accept the following values:
        if MINimum sets or queries the minimum amplitude level.
        if MAXimum sets or queries the maximum amplitude level.
        if DEFault sets the default amplitude level (2V).
        """,
    )
    
    offset_chn1 = Instrument.control(
        "SEQuence:ELEM1:OFFset1?", "SEQuence:ELEM1:OFFset1 %s",
        """ Sets or returns the voltage offset for the element
        “n=1” of the channel “m=1”.
        
        Apart from the offset in volts it can also accept the following values:
        MINimum sets or queries the minimum offset level.
        MAXimum sets or queries the maximum offset level.
        DEFault sets the default offset level (0V).
        """,
    )
    
    length_chn1 = Instrument.control(
        "SEQuence:ELEM1:LENGth?", "SEQuence:ELEM1:LENGth %s",
        """ Sets or returns the number of samples of the waveform
        for the element “n”.
        Apart from the length it can also accept the following values:
        MINimum sets or queries the minimum value of length.
        MAXimum sets or queries the maximum value of length.
        DEFault sets the default value of length (2048).
        """,
    )
    
    loop_count_chn1 = Instrument.control(
        "SEQuence:ELEM1:LOOP:COUNt?", "SEQuence:ELEM1:LOOP:COUNt %s",
        """ Sets or returns the number of samples of the waveform
        for the element “n”.
        Apart from the loop count it can also accept the following values:
        MINimum sets or queries the minimum value of repetitons parameter.
        MAXimum sets or queries the maximum value of repetitons
        parameter.
        INFinite sets infinite repetitons.
        DEFault sets the default value of repetition (1).
        """,
    )
    
    waveform_chn1 = Instrument.control(
        "SEQuence:ELEM1:WAVeform1?",
        "SEQuence:ELEM1:WAVeform1 \"%s\"",
        """This command sets or returns the waveform for the sequence
        element n=1. The value of m=1 indicates the channel that will output
        the waveform when the sequence is run. It’s possible select a
        waveform only from those in the waveform list. In waveform list are
        already present 10 predefined waveform: Sine, Ramp, Square, Sync,
        DC, Gaussian, Lorentz, Haversine, Exp_Rise and Exp_Decay but user
        can import in the list others customized waveforms.
        """,
    )
    
    output_chn2 = Instrument.control(
        get_command="OUTPut2:STATe?",
        set_command="OUTPut2:STATe %s",
        docs=""" A boolean property that turns on (True, 'on') or off (False, 'off')
        the output of the function generator. Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'ON', 'on': 'ON', 'ON' : 'ON', 1: 'ON',
                False: 'OFF', 'off': 'OFF', 'OFF': 'OFF', 0: 'OFF'}
    )
    
    output_load_chn2 = Instrument.control(
        "OUTPut2:SERIESIMPedance?", "OUTPut2:SERIESIMPedance %s",
        """ Sets the expected load resistance (should be the load impedance connected
        to the output. The output impedance is always 50 Ohm, this setting can be used
        to correct the displayed voltage for loads unmatched to 50 Ohm.
        Valid values are 50Ohm or 5Ohm.
        No validator is used since both numeric and string inputs are accepted,
        thus a value outside the range will not return an error.
        Can be set. """,
        validator=strict_discrete_set,
        values=['50Ohm','LOW']
    )
    
    voltage_high_chn2 = Instrument.control(
        "SEQuence:ELEM1:VOLTage:HIGH2?", "SEQuence:ELEM1:VOLTage:HIGH2 %s",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -3 V to 3 V (must be higher than low
        voltage by at least 1 mV). Can be set. """,
        validator=strict_range,
        values=[-3, 3],
    )
    
    voltage_low_chn2 = Instrument.control(
        "SEQuence:ELEM1:VOLTage:LOW2?", "SEQuence:ELEM1:VOLTage:LOWyyy %s",
        """ A floating point property that controls the upper voltage of the
        output waveform in V, from -3 V to 3 V (must be higher than low
        voltage by at least 1 mV). Can be set. """,
        validator=strict_range,
        values=[-3, 3],
    )
    
    amplitude_chn2 = Instrument.control(
        "SEQuence:ELEM1:AMPlitude2?", "SEQuence:ELEM1:AMPlitude2 %s",
        """ Sets or returns the voltage peak-to-peak amplitude for the element
        “n=1” of the channel “m=2”.
        
        Apart from the amplitude in volts it can also accept the following values:
        if MINimum sets or queries the minimum amplitude level.
        if MAXimum sets or queries the maximum amplitude level.
        if DEFault sets the default amplitude level (2V).
        """,
    )
    
    offset_chn2 = Instrument.control(
        "SEQuence:ELEM1:OFFset2?", "SEQuence:ELEM1:OFFset2 %s",
        """ Sets or returns the voltage offset for the element
        “n=1” of the channel “m=2”.
        
        Apart from the offset in volts it can also accept the following values:
        MINimum sets or queries the minimum offset level.
        MAXimum sets or queries the maximum offset level.
        DEFault sets the default offset level (0V).
        """,
    )
    
    length_chn2 = Instrument.control(
        "SEQuence:ELEM1:LENGth?", "SEQuence:ELEM1:LENGth %s",
        """ Sets or returns the number of samples of the waveform
        for the element “n”.
        Apart from the length it can also accept the following values:
        MINimum sets or queries the minimum value of length.
        MAXimum sets or queries the maximum value of length.
        DEFault sets the default value of length (2048).
        """,
    )
    
    loop_count_chn2 = Instrument.control(
        "SEQuence:ELEM1:LOOP:COUNt?", "SEQuence:ELEM1:LOOP:COUNt %s",
        """ Sets or returns the number of samples of the waveform
        for the element “n”.
        Apart from the loop count it can also accept the following values:
        MINimum sets or queries the minimum value of repetitons parameter.
        MAXimum sets or queries the maximum value of repetitons
        parameter.
        INFinite sets infinite repetitons.
        DEFault sets the default value of repetition (1).
        """,
    )
    
    waveform_chn2 = Instrument.control(
        "SEQuence:ELEM1:WAVeform2?",
        "SEQuence:ELEM1:WAVeform2 \"%s\"",
        """This command sets or returns the waveform for the sequence
        element n=1. The value of m=2 indicates the channel that will output
        the waveform when the sequence is run. It’s possible select a
        waveform only from those in the waveform list. In waveform list are
        already present 10 predefined waveform: Sine, Ramp, Square, Sync,
        DC, Gaussian, Lorentz, Haversine, Exp_Rise and Exp_Decay but user
        can import in the list others customized waveforms.
        """,
    )
    
def upload_signal_teledyne(awg,
                           name,
                           samples,
                           amp,
                           fs=None, # The sample rate is the same for both channels
                           channel=1,
                           run=False #If True the AWG will automatically run
                          ):
    """
    Uploads the signal to the Teledyne AWG.
    This are the followed steps.
    1) Disable the channel output. 
    2) Configure the channel.
    3) Upload waveform
    4) Selects waveform for channel
    5) Enable the channel output.
    
    Args:
        awg: The awg object.
        name (string): Name of the waveform. Recomended "temp1" for channel 1 and "temp2" for channel 2.
        samples (numpy array of floats): The samples of the signal.
        amp (float): The amplitude of the signal. Values selected are [-3,3]V
        fs (float): Sampling frequency (Hz). The number of samples per second.
        channel (int): Selected channel.
        run (Boolean): Run.
    """
    samples = np.concatenate([samples,[100]])
    awg.stop()
    awg.display_unit_volt = 'HIGH'
    awg.upload_waveform(name,samples,None)
    
    if fs is not None:
        awg.arb_srate=fs
    
    setattr(awg,'output_chn{}'.format(channel),'off')
    setattr(awg,'output_load_chn{}'.format(channel),'50Ohm')
    setattr(awg,'voltage_high_chn{}'.format(channel),amp)
    setattr(awg,'voltage_low_chn{}'.format(channel),0)
    setattr(awg,'waveform_chn{}'.format(channel),name)
    setattr(awg,'length_chn{}'.format(channel),len(samples)-1)
    setattr(awg,'output_chn{}'.format(channel),'on')
    
    if run:
        awg.run()