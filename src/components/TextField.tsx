import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
  control: {
    display: 'flex',
    flexDirection: 'row',
    border: (props: TextFieldProps) =>
      `1px solid ${props.outlineColor || '#808080'}`,
    alignItems: 'stretch'
  },
  input: {
    flex: 1,
    background: 'none',
    border: 'none',
    outline: 'none',
    padding: '8px',
    minWidth: 0
  },
  block: {
    width: '100%'
  }
});

interface TextFieldProps {
  outlineColor?: string;
  block?: boolean;
  before?: any;
  after?: any;
}

type MyProps = TextFieldProps & React.InputHTMLAttributes<HTMLInputElement>;

export const TextField: React.FC<MyProps> = ({
  block,
  before,
  after,
  ...props
}) => {
  const classes = useStyles(props);

  const inputClasses = [classes.input];
  if (block) {
    inputClasses.push(classes.block);
  }

  return (
    <div className={classes.control}>
      {before}
      <input type="text" className={inputClasses.join(' ')} {...props} />
      {after}
    </div>
  );
};
