/* These are commands used for creating some databases we might use in the beginning and inserting sample data.
 */

CREATE TABLE Courses (
  CourseID varchar(10) NOT NULL,
  CourseTitle varchar(255) NOT NULL,
/*  'CourseBook' varchar(255) NOT NULL*/
  PRIMARY KEY (CourseID) /*Or BISBN*/);


CREATE TABLE Books (
  BISBN varchar(255) NOT NULL,
  BTitle varchar(255) NOT NULL,
  BAuthor varchar(255) NOT NULL,
  BCourse varchar(10) NOT NULL,
  BPic varchar(255), /*a place holder for storing references to potentially more than one pictures*/
  BNumber INT, /*BNumber represents the number of books, rather than some kind of identity*/
  PRIMARY KEY (BISBN),
  FOREIGN KEY (BCourse) REFERENCES Courses(CourseID));


CREATE TABLE Users (
  UserID varchar(20) NOT NULL,
  UEmail varchar(30) NOT NULL,
  UPassword varchar(255) NOT NULL,
  IsAdmin tinyint(1) NOT NULL DEFAULT 0, /*Newly added to check the status of users*/
  UBooks varchar(255),
  UOtherInfo varchar(255),
  PRIMARY KEY (UserID)
/*  FOREIGN KEY (UBooks) REFERENCES Books(BISBN)*/ /*this may not work if Users have posted more than one book, or user did not post any book*/
  );


CREATE TABLE Postings (
  UserID varchar(20) NOT NULL,
  UBooks varchar(255) NOT NULL,
  PostDates varchar(255) NOT NULL /*used varchar rather than date data type because may contain more than one dates in each*/
  /*PRIMARY KEY (UserID)*/ /*might not be used as primary key if multiple rows are used*/
  /*FOREIGN KEY (UBooks) REFERENCES Books(BISBN)*/ /*this may not work if Users have posted more than one book*/
  );

COMMIT;


/*These data do not containing book info, so might not be used yet*/
INSERT INTO Courses VALUES
('COMP-1000', 'Key Concepts in Computer Science'),
('COMP-1400', 'Introduction to Algorithms and Programming I'),
('COMP-1410', 'Introduction to Algorithms and Programming II'),
('COMP-2120', 'Object-Oriented Programming Using Java'),
('COMP-2140', 'Computer Languages, Grammars, and Translators'),
('COMP-2310', 'Theoretical Foundations of Computer Science'),
('COMP-2540', 'Data Structures and Algorithms'),
('COMP-2560', 'Systems Programming'),
('COMP-2650', 'Computer Architecture I: Digital Design'),
('COMP-2660', 'Computer Architecture II: Microprocessor Programming'),
('COMP-2800', 'Software Development'),
('COMP-3110', 'Introduction to Software Engineering'),
('COMP-3150', 'Database Management Systems'),
('COMP-3220', 'Object-Oriented Software Analysis and Design'),
('COMP-3300', 'Operating Systems Fundamentals'),
('COMP-3340', 'World Wide Web Information Systems Development'),
('COMP-3400', 'Advanced Object Oriented System Design Using C++'),
('COMP-3500', 'Introduction to Multimedia Systems'),
('COMP-3520', 'Introduction to Computer Graphics'),
('COMP-3540', 'Theory of Computation'),
('COMP-3670', 'Computer Networks'),
('COMP-3680', 'Network Practicum'),
('COMP-3710', 'Artificial Intelligence Concepts'),
('COMP-3770', 'Game Design, Development and Tools'),
('COMP-4110', 'Software Verification and Testing'),
('COMP-4150', 'Advanced and Practical Database Systems'),
('COMP-4200', 'Mobile Application Development'),
('COMP-4220', 'Agile Software Development'),
('COMP-4250', 'Big Data Analytics and Database Design'),
('COMP-4400', 'Principles of Programming Languages'),
('COMP-4500', 'Multimedia System Development'),
('COMP-4540', 'Design and Analysis of Computer Algorithms'),
('COMP-4670', 'Network Security'),
('COMP-4680', 'Advanced Networking'),
('COMP-4700', 'Project Using Selected Tools'),
('COMP-4730', 'Advanced Topics in Artificial Intelligence I'),
('COMP-4740', 'Advanced Topics in Artificial Intelligence II'),
('COMP-4770', 'Artificial Intelligence for Games'),
('COMP-4800', 'Selected Topics in Software Engineering'),
('COMP-4960', 'Research Project'),
('COMP-4990', 'Project Management: Techniques and Tools'),
('MATH-1020', 'Mathematical Foundations'),
('MATH-1250', 'Linear Algebra I'),
('MATH-1260', 'Vectors and Linear Algebra'),
('MATH-1270', 'Linear Algebra (Engineering)'),
('MATH-1280', 'Access to Linear Algebra'),
('MATH-1720', 'Differential Calculus'),
('MATH-1730', 'Integral Calculus'),
('MATH-1760', 'Functions and Differential Calculus'),
('MATH-1780', 'Access to Differential Calculus'),
('MATH-1980', 'Mathematics for Business'),
('MATH-2250', 'Linear Algebra II'),
('MATH-2251', 'Linear Algebra III'),
('MATH-2780', 'Vector Calculus'),
('MATH-2790', 'Differential Equations'),
('MATH-3150', 'Introduction to Graph Theory'),
('MATH-3160', 'Combinatorics'),
('MATH-3200', 'Abstract Algebra'),
('MATH-3270', 'Number Theory'),
('MATH-3550', 'Introduction to Fourier Series and Special Functions'),
('MATH-3580', 'Introduction to Analysis I'),
('MATH-3581', 'Introduction to Analysis II'),
('MATH-3590', 'Complex Variables'),
('MATH-3800', 'Numerical Methods'),
('MATH-3940', 'Numerical Analysis for Computer Scientists'),
('MATH-3960', 'Linear Optimization'),
('MATH-3980', 'Theory of Interest'),
('MATH-4000', 'Topics in Mathematics'),
('MATH-4220', 'Introduction to Group Theory'),
('MATH-4230', 'Introduction to Field Theory'),
('MATH-4300', 'General Topology'),
('MATH-4570', 'Functional Analysis'),
('MATH-4580', 'Measure Theory and Integration'),
('MATH-4581', 'Real Analysis II'),
('MATH-4960', 'Portfolio Optimization'),
('MATH-4980', 'Actuarial Mathematics I'),
('MATH-4981', 'Actuarial Mathematics II'),
('STAT-2910', 'Statistics for the Sciences'),
('STAT-2920', 'Introduction to Probability'),
('STAT-2950', 'Introduction to Statistics'),
('STAT-3920', 'Probability'),
('STAT-3950', 'Statistics'),
('STAT-3960', 'Stochastic Operations Research'),
('STAT-4000', 'Topics in Statistics'),
('STAT-4200', 'Actuarial Regression and Time Series'),
('STAT-4410', 'Stochastic Processes'),
('STAT-4460', 'Statistical Data Analysis'),
('STAT-4470', 'Survival Analysis'),
('STAT-4500', 'Generalized Linear Models'),
('STAT-4490', 'Discrete Multivariate Analysis'),
('STAT-4550', 'Regression Analysis'),
('STAT-4980', 'Experimental Designs'),
('STAT-4981', 'Sampling Theory');
COMMIT;
