import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  control: {
    display: 'flex',
    flexDirection: 'row',
    border: (props: TextFieldProps) => `1px solid ${props.outlineColor || 'var(--jp-border-color1)'}`,
    alignItems: 'stretch'
  },
  input: {
    flex: 1,
    background: 'none',
    border: 'none',
    outline: 'none',
    padding: '8px',
    minWidth: 0,
    color: (props: TextFieldProps) => props.color || 'var(--jp-ui-font-color1)'
  },
  block: {
    width: '100%'
  }
});

interface TextFieldProps {
  outlineColor?: string;
  color?: string;
  block?: boolean;
  before?: any;
  after?: any;
}

type MyProps = TextFieldProps & React.InputHTMLAttributes<HTMLInputElement>;

const _TextField = (props: MyProps, ref: React.Ref<HTMLInputElement>) => {
  const { block, before, after, outlineColor, className, ...carriedProps } = props;
  const classes = useStyles({ outlineColor });

  const inputClasses = [classes.input];
  if (block) {
    inputClasses.push(classes.block);
  }
  return (
    <div className={classes.control}>
      {before}
      <input ref={ref} type="text" className={inputClasses.join(' ') + ' ' + className || ''} {...carriedProps} />
      {after}
    </div>
  );
};

export const TextField = React.forwardRef(_TextField);
