import React from 'react';
import { createUseStyles } from 'react-jss';

const useStyles = createUseStyles({
    tab: {
        borderBottom: '1px solid #e0e0e0',
        listStyleType: 'none',
        margin: 0,
        padding: '0 8px 0 8px',
        overflow: 'hidden'
    },
    tabItem: {
        float: 'left',
        display: 'block',
        padding: '12px',
        textTransform: 'uppercase',
        borderRadius: '4px 4px 0 0',
        fontSize: '10pt',
        cursor: 'pointer',
        '&:hover': {
            background: '#f9f9f9'
        },
        '&.active': {
            background: '#f0f0f0',
            fontWeight: 'bold'
        },
    },
    tabItemRight: {
        extend: 'tabItem',
        float: 'right'
    }
});

interface MenuBarProps {
    value?: any;
    onChange: { (value: any): void };
    menus: Menu[];
}

export interface Menu {
    title: any;
    value: any;
    right?: boolean;
}

export const MenuBar: React.FunctionComponent<MenuBarProps> = ({ menus, value, onChange }) => {
    const classes = useStyles();

    const handleClick = (value: any) => {
        console.log(value);
        onChange(value);
    };

    return (
        <div>
            <ul className={classes.tab}>
                { menus.map(menu => {
                    const activeClass = menu.value === value ? 'active' : '';
                    const tabClass = menu.right ? classes.tabItemRight : classes.tabItem;
                    return (
                        <li onClick={() => handleClick(menu.value)} key={menu.value} className={`${tabClass} ${activeClass}`}>
                            { menu.title }
                        </li>
                    );
                }) }
            </ul>
        </div>
    );
}