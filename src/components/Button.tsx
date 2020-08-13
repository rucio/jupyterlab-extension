import React from 'react';
import { createUseStyles } from 'react-jss';

interface ButtonProps {
  onClick?: { (): void };
  color?: string;
  hoverTextColor?: string;
  hoverBackgroundColor?: string;
  outlineColor?: string;
  block?: boolean;
}

const useStyles = createUseStyles({
  button: {
    background: 'none',
    padding: 0,
    border: '1px solid',
    borderColor: (props: ButtonProps) => `${props.outlineColor || 'var(--jp-border-color1)'}`,
    color: (props: ButtonProps) => props.color || 'var(--jp-ui-font-color1)',
    outline: 'none',
    cursor: 'pointer',
    borderRadius: '2px',
    '&:hover': {
      backgroundColor: (props: ButtonProps) => `${props.hoverBackgroundColor || 'var(--jp-layout-color2)'}`,
      borderColor: (props: ButtonProps) => `${props.outlineColor || 'var(--jp-border-color1)'}`,
      color: (props: ButtonProps) => `${props.color || props.hoverTextColor || 'var(--jp-ui-font-color1)'}`
    },
    '&:active': {
      backgroundColor: (props: ButtonProps) => `${props.hoverBackgroundColor || 'var(--jp-layout-color2)'}`
    },
    '&:disabled': {
      opacity: 0.5,
      cursor: 'inherit',
      '&:hover': {
        background: 'none',
        borderColor: (props: ButtonProps) => `${props.outlineColor || 'var(--jp-border-color1)'}`
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
