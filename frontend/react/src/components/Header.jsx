import React from "react";

const Header = ({ className = "", children, ...props }) => (
  <header className={`app__header ${className}`.trim()} {...props}>
    {children}
  </header>
);

export default Header;
