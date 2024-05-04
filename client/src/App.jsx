import React, { useState, useContext, createContext, useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, Navigate, useParams} from 'react-router-dom'
import './App.css'

const Context = createContext(null)

// Authentication helper function
function checkAuth(setIsLoggedIn) {
  fetch('/auth/check_auth', {
    credentials: 'include' 
  })
    .then(response => response.json())
    .then(data => setIsLoggedIn(data.isAuthenticated))
    .catch(error => {
      console.error('Error checking authentication:', error)
      setIsLoggedIn(false)
    })
}

// Login component
function Login() {
  const { isLoggedIn, setIsLoggedIn  } = useContext(Context)
  const navigate = useNavigate()
  const [userRole, setUserRole] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    checkAuth(isLoggedIn => {
      if (isLoggedIn){
        navigate('/dashboard')
      }
    })
  }, [isLoggedIn])

  const handleRoleSelect = (role) => {
      setUserRole(role)
    }

  const handleLogin = async () => {
    window.location = `/auth/login?role=${userRole}`
    setIsLoggedIn(true)
  }

  return (
    <div className="Login">
      {!userRole && (
        <div>
          <button className="button" onClick={() => handleRoleSelect('student')}>I'm a student</button>
          <button className="button" onClick={() => handleRoleSelect('instructor')}>I'm an instructor</button>
        </div>
      )}
      {userRole && (
        <>
          <button className="button" onClick={handleLogin}>Login</button>
          {errorMessage && <p className="error">{errorMessage}</p>}
        </>
      )}
    </div>
  )
}

// Dashboard component
function Dashboard() {
  const { isLoggedIn, setIsLoggedIn } = useContext(Context)
  const navigate = useNavigate()
  const [errorMessage, setErrorMessage] = useState('')
  const [userName, setUserName] = useState('')
  const [userRole, setUserRole] = useState('')
  const [courseName, setCourseName] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [courses, setCourses] = useState([])
  const [courseCode, setCourseCode] = useState('')

  useEffect(() => {
    checkAuth(isLoggedIn => {
      if (!isLoggedIn) {
        navigate('/')
      } else {
        fetchUserInfo()
      }
    })
  }, [isLoggedIn])
  
  const handleLogout = async () => {
    try {
      const response = await fetch('/auth/logout', {
        credentials: 'include' 
      })
      const data = await response.json()
      setIsLoggedIn(false)
      navigate('/')
    } catch (error) {
      console.error('Error during logout:', error)
      setErrorMessage('Error during logout. Please try again.')
    }
  }

  const fetchUserInfo = async () => {
    try {
      const response = await fetch('/api/user_info', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        if (data.name) {
          setUserName(data.name)
          setUserRole(data.role)
          setCourses(data.courses)
        } else {
          setUserName(null)
          setUserRole(null)
          setCourses([])
        }
      } else {
        throw new Error('Failed to fetch user info')
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
      setUserName(null)
      setUserRole(null)
      setCourses([])
    }
  }

  // replicate try catch, reponse.ok throw new error structure
  const handleCreateCourse = async () => {
    try {
      const response = await fetch('/api/create_course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ course_name: courseName })
      })
      const data = await response.json()
      if (response.ok) {
        alert(data.message)
        setCourseName('')
        setShowForm(false)
        setErrorMessage('')
        fetchUserInfo()
      } else {
        throw new Error(data.message || 'Failed to join course')
      }
    } catch (error) {
      console.error('Error creating course:', error)
      setErrorMessage(error.message)
    }
  }

  const handleJoinCourse = async () => {
    try {
      const response = await fetch('/api/join_course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ course_code: courseCode })
      })
      const data = await response.json()
      if (response.ok) {
        alert(data.message)
        setCourseCode('')
        setShowForm(false)
        setErrorMessage('')
        fetchUserInfo()
      } else {
        throw new Error(data.message || 'Failed to join course')
      }
    } catch (error) {
      console.error('Error joining course:', error)
      setErrorMessage(error.message)
    }
  }

  const handleCourseClick = (courseId) => {
    navigate(`/dashboard/${courseId}`)
  }

  const handleCancel = () => {
    setShowForm(false)
    setErrorMessage('')
  }

  return (
    <div>
      <h1>Dashboard</h1>
      {userName ? <h2>Welcome, {userName}</h2> : <p>'Failed to fetch user data.'</p>}
      {userRole === 'instructor' && !showForm && (
        <button className="button" onClick={() => setShowForm(true)}>Create Course</button>
      )}
      {userRole === 'instructor' && showForm && (
        <>
          <input
            type="text"
            value={courseName}
            onChange={e => setCourseName(e.target.value)}
            placeholder="Enter course name"
          />
          <button className="button" onClick={handleCreateCourse}>Submit</button>
          <button className="button" onClick={handleCancel}>Cancel</button>
        </>
      )}
      {userRole === 'student' && !showForm && (
        <button className="button" onClick={() => setShowForm(true)}>Join Course</button>
      )}
      {userRole === 'student' && showForm && (
        <>
          <input
            type="text"
            value={courseCode}
            onChange={e => setCourseCode(e.target.value)}
            placeholder="Enter course code"
          />
          <button className="button" onClick={handleJoinCourse}>Submit</button>
          <button className="button" onClick={handleCancel}>Cancel</button>
        </>
      )}
      <button className="button" onClick={handleLogout}>Logout</button>
      {errorMessage && <p className="error">{errorMessage}</p>}
      <h2>Your Courses</h2>
      <ul className="student-list">
        {courses.map(course => (
          <li key={course.id} className="student-card">
            <span className="student-info">
              {course.name}
            </span>
            <button className="button" onClick={() => handleCourseClick(course.id)}>
                {userRole === 'instructor' ? 'Manage' : 'View'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

function Course() {
  const { isLoggedIn, setIsLoggedIn } = useContext(Context)
  const { courseId } = useParams()
  const navigate = useNavigate()
  const [userId, setUserId] = useState('')
  const [userRole, setUserRole] = useState('')
  const [courseExists, setCourseExists] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [courseName, setCourseName] = useState('')
  const [courseCode, setCourseCode] = useState('')
  const [instructorDetails, setInstructorDetails] = useState({})
  const [students, setStudents] = useState([])
  const [sessionCode, setSessionCode] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [sessionActive, setSessionActive] = useState(false)
  const [showQRCode, setShowQRCode] = useState(false)
  const [qrCodeUrl, setQRCodeURL] = useState('')
  const [attendCode, setAttendCode] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [attendanceInfo, setAttendanceInfo] = useState({ totalAttendance: 0, totalSessions: 0, attendanceRatio: 0 })

  useEffect(() => {
    checkAuth(isLoggedIn => {
      if (!isLoggedIn) {
        navigate('/')
      }
    })
  }, [isLoggedIn])

  useEffect(() => {
    checkUserInfo(), fetchCourseDetails(courseId)
  }, [])

  useEffect(() => {
    if (userId) {
      fetchAttendanceData()
    }
  }, [userId])

  useEffect(() => {
    const setupCourse = async () => {
      const isActiveSession = await fetchSessionStatus()
      setSessionActive(isActiveSession)
    } 
    setupCourse()
  }, [])

  useEffect(() => {
    if (userRole === 'instructor') {
      fetchSessionStatus()
    }
  }, [courseId])

  const checkUserInfo = async () => {
    try {
      const response = await fetch('/api/user_info', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setUserId(data.id)
        setUserRole(data.role)
        const courseFound = data.courses && data.courses.some(course => course.id.toString() === courseId)
        setCourseExists(courseFound)
      } else {
        throw new Error('Failed to fetch user info')
      }
    } catch (error) {
      console.error('Error fetching course info:', error)
      setCourseExists(false)
    }
  }

  const fetchCourseDetails = async (courseId) => {
    try {
      const response = await fetch(`/api/course_details/${courseId}`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setCourseName(data.name)
        setCourseCode(data.code)
        setInstructorDetails(data.instructor)
        setStudents(data.students)
      } else {
        throw new Error('Failed to fetch course details')
      }
    } catch (error) {
      console.error('Error fetching course details:', error)
      setErrorMessage(error.message)
    }
  }
  
  const fetchAttendanceData = async () => {
    try {
      const response = await fetch(`/api/student_attendance?user_id=${userId}&course_id=${courseId}`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setAttendanceInfo({
          totalAttendance: data.total_attendance,
          totalSessions: data.total_sessions,
          attendanceRatio: data.attendance_ratio
        })
      } else {
        throw new Error('Failed to fetch attendance data')
      }
    } catch (error) {
      console.error('Error fetching attendance data:', error)
    }
  }


  const fetchSessionStatus = async () => {
    try {
      const response = await fetch(`/api/session_status/${courseId}`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setSessionCode(data.code)
        setStartTime(data.start_time)
        setEndTime(data.end_time)
        setSessionActive(data.is_active)
        return data.is_active
      } else {
        throw new Error('Failed to fetch session status')
      }
    } catch (error) {
      console.error('Error fetching session status:', error)
      setErrorMessage(error.message)
      return false
    }
  }
  
  const handleStartStopSession = async () => {
    const sessionIsActive = await fetchSessionStatus()
    if (sessionIsActive) {
      try {
        const response = await fetch('/api/end_session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({ user_id: userId, session_code: sessionCode })
        })
        const data = await response.json()
        if (!response.ok) {
          throw new Error(data.message || 'Failed to end session')
        }
        setSessionActive(false)
        setShowQRCode(false)
      } catch (error) {
        console.error('Error ending session:', error)
        setErrorMessage(error.message)
      }
    } else {
      try {
        const response = await fetch('/api/start_session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({ course_id: courseId })
        })
        const data = await response.json()
        if (response.ok) {
          setSessionActive(true)
          setSessionCode(data.code)
          setStartTime(data.start_time)
          setEndTime(data.end_time)
        } else {
          throw new Error(data.message || 'Failed to start session')
        }
      } catch (error) {
        console.error('Error starting session:', error)
        setErrorMessage(error.message)
      }
    }
  }
  
  const handleGenerateQRCode = () => {
    if (!showQRCode) {
      fetch(`/api/qr_code/${sessionCode}`)
        .then(response => {
          if (response.ok) {
            return response.blob()
          }
          throw new Error('Failed to generate QR code')
        })
        .then(blob => {
          const url = URL.createObjectURL(blob)
          setQRCodeURL(url)
          setShowQRCode(true)
        })
        .catch(error => console.error('Error:', error))
    } else {
      setShowQRCode(false);
    }
  }  

  const handleSubmitAttendance = async () => {
    try {
      const response = await fetch('/api/submit_attendence', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ user_id: userId, course_id: courseId, session_code: attendCode })
      })
      const data = await response.json()
      if (response.ok) {
        fetchAttendanceData()
        alert(data.message)
        setAttendCode('')
        setShowForm(false)
      } else {
        throw new Error(data.message || 'Failed to submit attendance')
      }
    } catch (error) {
      console.error('Error submitting attendance:', error)
      setErrorMessage(error.message)
    }
  }

  const handleDeleteCourse = async () => {
    try {
      const response = await fetch(`/api/delete_course`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ course_id: courseId })
      })
      const data = await response.json()
      if (response.ok) {
        alert(data.message)
        navigate('/dashboard')
      } else {
        throw new Error(data.message || 'Failed to delete course')
      }
    } catch (error) {
        console.error('Error deleting course:', error)
        setErrorMessage(error.message)
    }
  }

  const handleLeaveCourse = async () => {
    try {
      const response = await fetch(`/api/leave_course`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ course_id: courseId })
      })
      const data = await response.json()
      if (response.ok) {
        alert(data.message)
        navigate('/dashboard')
      } else {
        throw new Error(data.message || 'Failed to delete course')
      }
    } catch (error) {
        console.error('Error deleting course:', error)
        setErrorMessage(error.message)
    }
  }

  const handleRemoveStudent = async (studentId) => {
    try {
      const response = await fetch(`/api/remove_student`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ course_id: courseId, student_id: studentId })
      })
      const data = await response.json()
      if (response.ok) {
        fetchCourseDetails(courseId)
        alert(data.message)
      } else {
        throw new Error(data.message || 'Failed to remove student')
      }
    } catch (error) {
      console.error('Error removing student:', error)
      setErrorMessage(error.message)
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setErrorMessage('')
  }

  if (!courseExists) {
    return (
      <div>
        <h1>Course Not Available</h1>
        <p>This course is not available.</p>
        <button className="button" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
      </div>
    )
  }

  return (
    <div>
      <h1>{courseName}</h1>
      {userRole === 'instructor' && (
        <>
          <div className="course-info">
            <p><strong>Course Code: </strong>{courseCode}</p>
            <div className="control-buttons">
              <button className="button" onClick={handleDeleteCourse}>Delete Course</button>
              <button className="button" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
            </div>
          </div>
            {!sessionActive && (
                  <button className="button" onClick={handleStartStopSession}>
                    Start Attendance
                  </button>
            )}

          {errorMessage && <p className="error">{errorMessage}</p>}
          {sessionActive && (
            <div className="session-details">
              <button className="button" onClick={handleStartStopSession}>
                {sessionActive ? 'Stop Attendance' : 'Start Attendance'}
              </button>

              <button className="button" onClick={handleGenerateQRCode}>
                {showQRCode ? 'Hide QR Code' : 'Generate QR Code'}
              </button>
              {showQRCode && <img src={qrCodeUrl} alt="QR Code" />}
              
              <p className="session-info"><strong>Session Code: </strong>{sessionCode}</p>
              <p className="session-info"><strong>Time: </strong> {new Date(startTime).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', hour12: true})} - {new Date(endTime).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', hour12: true})}</p>
            </div>
          )}

          <h2>Your Students</h2>
          <ul className="student-list">
            {students.map((student) => (
              <li key={student.id} className="student-card">
                <span className="student-info">
                  {student.name}
                </span>
                <span className="student-info">
                  Attendance: {student.attendance.attended_sessions}/{student.attendance.total_sessions} ({(student.attendance.attendance_ratio * 100).toFixed(1)}%)
                </span>
                <button className="remove-button" onClick={() => handleRemoveStudent(student.id)}>Remove</button>
              </li>
            ))}
          </ul>
        </>
      )}


      {userRole === 'student' && (
        <>
          <div className="course-info">
            <p>Your Instructor: {instructorDetails.name}</p>
            <p>Your Attendance: {attendanceInfo.totalAttendance}/{attendanceInfo.totalSessions} ({(attendanceInfo.attendanceRatio * 100).toFixed(1)}%)</p>
            <div className="control-buttons">
              <button className="button" onClick={handleLeaveCourse}>Leave Course</button>
              <button className="button" onClick={() => navigate('/dashboard')}>Back to Dashboard</button>
            </div>
          </div>

          {showForm ? (
            <div>
              <input
                type="text"
                value={attendCode}
                onChange={e => setAttendCode(e.target.value)}
                placeholder="Enter session code"
                className="input"
              />
              <div className="control-buttons">
                <button className="button" onClick={handleSubmitAttendance}>Submit</button>
                <button className="button" onClick={handleCancel}>Cancel</button>
              </div>
            </div>
          ) : (
            <button className="button" onClick={() => setShowForm(true)}>Submit Attendance</button>
          )}

          {errorMessage && <p className="error">{errorMessage}</p>}
        </>
      )}

    </div>
  )
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  return (
    <Context.Provider value={{ isLoggedIn, setIsLoggedIn }}>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Login />} />
          <Route path='/dashboard' element={<Dashboard />} />
          <Route path='/dashboard/:courseId' element={<Course />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </Context.Provider>
  )
}

export default App