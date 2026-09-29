import React from 'react';
import { PinModal, PinModalProps } from '../common/PinModal';

export type PinVerificationDialogProps = PinModalProps;

export const PinVerificationDialog: React.FC<PinVerificationDialogProps> = (props) => {
  return <PinModal {...props} />;
};

export default PinVerificationDialog;
