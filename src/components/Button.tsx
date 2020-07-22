import React from 'react';
import { createUseStyles } from 'react-jss';

interface ButtonProps {
  onClick?: { (): void };
  color?: string;
  outlineColor?: string;
  block?: boolean;
}

const useStyles = createUseStyles({
  button: {
    background: 'none',
    padding: 0,
    border: '1px solid',
    borderColor: (props: ButtonProps) => `${props.outlineColor || '#000000'}90`,
    color: (props: ButtonProps) => props.color || '#000',
    outline: 'none',
    cursor: 'pointer',
    borderRadius: '2px',
    '&:hover': {
      backgroundColor: (props: ButtonProps) => `${props.outlineColor || '#000000'}09`,
      borderColor: (props: ButtonProps) => `${props.outlineColor || '#000000'}B0`
    },
    '&:active': {
      backgroundColor: (props: ButtonProps) => `${props.outlineColor || '#000000'}12`
    },
    '&:disabled': {
      opacity: 0.5,
      cursor: 'inherit',
      '&:hover': {
        background: 'none',
        borderColor: (props: ButtonProps) => `${props.outlineColor || '#000000'}90`
      },
      '&:active': {
        background: 'none'
      }
    }
  },
  block: {
    width: '100%',
    display: 'block'
  },
  childrenContainer: {
    margin: '8px 16px 8px 16px'
  }
});

type MyProps = ButtonProps & React.ButtonHTMLAttributes<HTMLButtonElement>;

export const Button: React.FC<MyProps> = ({ children, block, onClick, className, ...props }) => {
  const classes = useStyles(props);

  const btnClasses = [classes.button, className];
  if (block) {
    btnClasses.push(classes.block);
  }

  return (
    <button className={btnClasses.join(' ')} onClick={onClick} {...props}>
      <div className={classes.childrenContainer}>{children}</div>
    </button>
  );
};
