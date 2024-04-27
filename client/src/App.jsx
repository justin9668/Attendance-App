import React, { useState, useContext, createContext, useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, Navigate} from 'react-router-dom'
import './App.css'

const AuthContext = createContext(null)

function useAuth() {
  return useContext(AuthContext)
}

function checkAuth(setIsLoggedIn, setUserRole) {
  fetch('/auth/check_auth', {
    credentials: 'include' 
  })
    .then(response => response.json())
    .then(data => {
      if (data.isAuthenticated) {
        setIsLoggedIn(true)
        setUserRole(data.role)
      } else {
        setIsLoggedIn(false)
        setUserRole(null)
      }
    })
    .catch(error => {
      console.error('Error checking authentication:', error)
      setIsLoggedIn(false)
      setUserRole(null)
    })
}

function Login() {
  const { setIsLoggedIn } = useAuth()
  const navigate = useNavigate()
  const [userRole, setUserRole] = useState('') // frontend role state
  const [errorMessage, setErrorMessage] = useState('')

  // consider deleting
  useEffect(() => {
    checkAuth(isLoggedIn => {
      if (isLoggedIn) {
        navigate('/dashboard')
      }
    }) // issue here
  }, [navigate])

  const handleRoleSelect = (role) => {
    setUserRole(role)
  }

  const handleLogin = async () => {
    window.location = `/auth/login?role=${userRole}`
    setIsLoggedIn(true)
  }

  return (
    <div className="Login">
      {userRole === '' && (
        <div>
          <button onClick={() => handleRoleSelect('student')}>I'm a student</button>
          <button onClick={() => handleRoleSelect('instructor')}>I'm an instructor</button>
        </div>
      )}
      {userRole !== '' && (
        <>
          <button onClick={handleLogin}>Login</button>
          {errorMessage && <p className="error">{errorMessage}</p>}
        </>
      )}
    </div>
  )
}

function Dashboard() {
  const { setIsLoggedIn } = useAuth()
  const navigate = useNavigate()
  const [errorMessage, setErrorMessage] = useState('')
  const [userName, setUserName] = useState('')
  const [userRole, setUserRole] = useState('') // backend role state
  const [classroomName, setClassroomName] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [classes, setClasses] = useState([])

  useEffect(() => {
    checkAuth(isLoggedIn => {
      if (!isLoggedIn) {
        navigate('/')
      } else {
        fetchUserInfo()
      }
    }, setUserRole)
  }, [navigate])
  
  const handleLogout = async () => {
    try {
      const response = await fetch('/auth/logout', {
        credentials: 'include' 
      })
      const data = await response.json()
      setIsLoggedIn(false)
      alert(data.message)
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
          if (data.role === 'instructor' || data.role === 'student') {
            setClasses(data.classes)
          }
        } else {
          setUserName(null)
          setUserRole(null)
          setClasses([])
        }
      } else {
        throw new Error('Failed to fetch user info');
      }
    } catch (error) {
      console.error('Error fetching user info:', error)
      setUserName(null)
      setUserRole(null)
      setClasses([])
    }
  }

  // replicate try catch, reponse.ok throw new error structure
  const handleCreateClass = async () => {
    try {
      const response = await fetch('/api/create_classroom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ classroom_name: classroomName })
      })
      if (response.ok) {
        const data = await response.json()
        alert('Class created: ' + data.name)
        setClassroomName('')
        setShowForm(false)
        fetchUserInfo()
      } else {
        throw new Error('Failed to create class: ' + response.status);
      }
    } catch (error) {
      console.error('Error creating classroom:', error);
      setErrorMessage('Failed to create class. Please try again.');
    }
  }

  return (
    <div>
    <h1>Dashboard</h1>
    {userName ? <h2>Welcome, {userName}</h2> : <p>'Failed to fetch user data.'</p>}
    {userRole === 'instructor' && !showForm && (
      <button onClick={() => setShowForm(true)}>Create Class</button>
    )}
    {userRole === 'instructor' && showForm && (
      <>
        <input
          type="text"
          value={classroomName}
          onChange={e => setClassroomName(e.target.value)}
          placeholder="Enter class name"
        />
        <button onClick={handleCreateClass}>Submit</button>
        <button onClick={() => setShowForm(false)}>Cancel</button>
      </>
    )}
    {userRole === 'student' && <button>Join Class</button>}
    <button onClick={handleLogout}>Logout</button>
    {errorMessage && <p className="error">{errorMessage}</p>}
    <h3>Your Classes</h3>
    <ul> 
      {classes.map(classroom => (
        <li key={classroom.id}>{classroom.name}</li>
      ))}
    </ul>
  </div>
  )
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  return (
    <AuthContext.Provider value={{ isLoggedIn, setIsLoggedIn }}>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Login />} />
          <Route path='/dashboard' element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  )
}

export default App